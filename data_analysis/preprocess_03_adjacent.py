"""
인접 플로우(과거1/과거2) 피처 결합 데이터셋 생성

기준 논문: NF-UQ-NIDS-v2 시계열 정보 보완 (인접 플로우 = 동일 IPV4_SRC_ADDR,
시간순서상 직전 2개 플로우, 10,000 플로우 이내, 부족 시 미래로 대체, 둘 다 없으면 0)

대상 클래스(5종 공격, Benign 제외): scanning, reconnaissance, xss, password, injection
"""
import os
import sys
import time
import warnings
from datetime import datetime

import duckdb
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════
# 설정
# ══════════════════════════════════════════════════════════════
TEST_MODE = False  # True: sample_2M.csv로 검증, False: 원본 76M 전체 실행

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

RAW_FILE = 'sample_2M.csv' if TEST_MODE else 'NF-UQ-NIDS-v2.csv'
RAW_PATH = os.path.join(DATA_DIR, RAW_FILE)
DB_PATH = os.path.join(DATA_DIR, 'adjacent_pipeline.duckdb')

OUT_SAMPLED_PATH = os.path.join(DATA_DIR, 'adjacent_sampled.csv')
OUT_CLEANED_PATH = os.path.join(DATA_DIR, 'adjacent_cleaned.csv')
OUT_FINAL_PATH = os.path.join(DATA_DIR, 'adjacent_final.csv')

TARGET_CLASSES = ['scanning', 'reconnaissance', 'xss', 'password', 'injection']
GAP_LIMIT = 10000
SAMPLE_PER_CLASS = 5000 if TEST_MODE else 200_000  # 클래스별 언더샘플링 목표 행 수

# 원본 46컬럼 중 Label/Attack/Dataset을 제외한 43개 ("논문의 43개 피처")
BASE_COLS = [
    'IPV4_SRC_ADDR', 'L4_SRC_PORT', 'IPV4_DST_ADDR', 'L4_DST_PORT',
    'PROTOCOL', 'L7_PROTO', 'IN_BYTES', 'IN_PKTS', 'OUT_BYTES', 'OUT_PKTS',
    'TCP_FLAGS', 'CLIENT_TCP_FLAGS', 'SERVER_TCP_FLAGS',
    'FLOW_DURATION_MILLISECONDS', 'DURATION_IN', 'DURATION_OUT', 'MIN_TTL', 'MAX_TTL',
    'LONGEST_FLOW_PKT', 'SHORTEST_FLOW_PKT', 'MIN_IP_PKT_LEN', 'MAX_IP_PKT_LEN',
    'SRC_TO_DST_SECOND_BYTES', 'DST_TO_SRC_SECOND_BYTES',
    'RETRANSMITTED_IN_BYTES', 'RETRANSMITTED_IN_PKTS',
    'RETRANSMITTED_OUT_BYTES', 'RETRANSMITTED_OUT_PKTS',
    'SRC_TO_DST_AVG_THROUGHPUT', 'DST_TO_SRC_AVG_THROUGHPUT',
    'NUM_PKTS_UP_TO_128_BYTES', 'NUM_PKTS_128_TO_256_BYTES', 'NUM_PKTS_256_TO_512_BYTES',
    'NUM_PKTS_512_TO_1024_BYTES', 'NUM_PKTS_1024_TO_1514_BYTES',
    'TCP_WIN_MAX_IN', 'TCP_WIN_MAX_OUT',
    'ICMP_TYPE', 'ICMP_IPV4_TYPE', 'DNS_QUERY_ID', 'DNS_QUERY_TYPE', 'DNS_TTL_ANSWER',
    'FTP_COMMAND_RET_CODE',
]
assert len(BASE_COLS) == 43

# 과거1/과거2 블록에서는 IP 주소 문자열 제외 (어차피 클리닝 단계에서 드롭, 타입충돌 방지)
PAST_COLS = [c for c in BASE_COLS if c not in ('IPV4_SRC_ADDR', 'IPV4_DST_ADDR')]
assert len(PAST_COLS) == 41

# ══════════════════════════════════════════════════════════════
# 로그 세팅
# ══════════════════════════════════════════════════════════════
_script = os.path.splitext(os.path.basename(__file__))[0]
_ts = datetime.now().strftime('%Y%m%d_%H%M')
LOG_PATH = os.path.join(LOG_DIR, f'{_script}_{_ts}.txt')


class _Tee:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, msg):
        for s in self._streams:
            s.write(msg)

    def flush(self):
        for s in self._streams:
            s.flush()


_log_file = open(LOG_PATH, 'w', encoding='utf-8')
sys.stdout = _Tee(sys.__stdout__, _log_file)
print(f"로그 저장: {LOG_PATH}")
print(f"TEST_MODE={TEST_MODE}, RAW_PATH={RAW_PATH}\n")

# ══════════════════════════════════════════════════════════════
# DuckDB 연결
# ══════════════════════════════════════════════════════════════
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
con = duckdb.connect(DB_PATH)
con.execute("PRAGMA threads=1")          # row_number()가 원본 파일 순서를 그대로 따르도록 단일 스레드
con.execute("PRAGMA memory_limit='10GB'")

target_list = ", ".join(f"'{c}'" for c in TARGET_CLASSES)

# ══════════════════════════════════════════════════════════════
# Step 1. 5종 공격 필터 + time_idx(=원본 파일 내 등장 순서) 부여
# ══════════════════════════════════════════════════════════════
print("[Step 1] 5종 공격 필터 + time_idx 부여")
t0 = time.time()
con.execute("DROP TABLE IF EXISTS attack5")
con.execute(f"""
    CREATE TABLE attack5 AS
    SELECT {', '.join(BASE_COLS)}, Attack,
           row_number() OVER () AS time_idx
    FROM read_csv_auto('{RAW_PATH}')
    WHERE lower(Attack) IN ({target_list})
""")
n_attack5 = con.execute("SELECT count(*) FROM attack5").fetchone()[0]
print(f"  -> {n_attack5:,}행  ({time.time()-t0:.1f}초)")

print("\n  클래스별 분포:")
print(con.execute("SELECT lower(Attack) AS attack, count(*) cnt FROM attack5 GROUP BY 1 ORDER BY 2 DESC").df())

print("\n  IP별 그룹 수:", con.execute("SELECT count(DISTINCT IPV4_SRC_ADDR) FROM attack5").fetchone()[0])

# ══════════════════════════════════════════════════════════════
# Step 2~4. IP별 LAG/LEAD 계산 -> 과거1/과거2/GAP_TO_PAST1 결정
# ══════════════════════════════════════════════════════════════
print("\n[Step 2-4] 인접 플로우(과거1/과거2/GAP_TO_PAST1) 계산")
t0 = time.time()

win_exprs = []
for c in PAST_COLS + ['time_idx']:
    win_exprs.append(f"LAG({c},1) OVER w AS lag1_{c}")
    win_exprs.append(f"LAG({c},2) OVER w AS lag2_{c}")
    win_exprs.append(f"LEAD({c},1) OVER w AS lead1_{c}")
    win_exprs.append(f"LEAD({c},2) OVER w AS lead2_{c}")

current_select = [f"sub.{c} AS {c}" for c in BASE_COLS] + ["sub.Attack AS Attack"]

past1_select, past2_select = [], []
for c in PAST_COLS:
    past1_select.append(f"""CASE
        WHEN sub.lag1_time_idx IS NOT NULL AND (sub.time_idx - sub.lag1_time_idx) <= {GAP_LIMIT} THEN sub.lag1_{c}
        WHEN sub.lead1_time_idx IS NOT NULL AND (sub.lead1_time_idx - sub.time_idx) <= {GAP_LIMIT} THEN sub.lead1_{c}
        ELSE 0
    END AS past1_{c}""")
    past2_select.append(f"""CASE
        WHEN sub.lag2_time_idx IS NOT NULL AND (sub.time_idx - sub.lag2_time_idx) <= {GAP_LIMIT} THEN sub.lag2_{c}
        WHEN sub.lead2_time_idx IS NOT NULL AND (sub.lead2_time_idx - sub.time_idx) <= {GAP_LIMIT} THEN sub.lead2_{c}
        ELSE 0
    END AS past2_{c}""")

gap_expr = f"""CASE
    WHEN sub.lag1_time_idx IS NOT NULL AND (sub.time_idx - sub.lag1_time_idx) <= {GAP_LIMIT} THEN (sub.time_idx - sub.lag1_time_idx)
    WHEN sub.lead1_time_idx IS NOT NULL AND (sub.lead1_time_idx - sub.time_idx) <= {GAP_LIMIT} THEN -(sub.lead1_time_idx - sub.time_idx)
    ELSE 0
END AS GAP_TO_PAST1"""

full_sql = f"""
CREATE TABLE attack5_adjacent AS
SELECT
  {', '.join(current_select)},
  {', '.join(past1_select)},
  {', '.join(past2_select)},
  {gap_expr}
FROM (
  SELECT *, {', '.join(win_exprs)}
  FROM attack5
  WINDOW w AS (PARTITION BY IPV4_SRC_ADDR ORDER BY time_idx)
) AS sub
"""
con.execute("DROP TABLE IF EXISTS attack5_adjacent")
con.execute(full_sql)
n_adj = con.execute("SELECT count(*) FROM attack5_adjacent").fetchone()[0]
n_cols = len(con.execute("SELECT * FROM attack5_adjacent LIMIT 0").df().columns)
print(f"  -> {n_adj:,}행 x {n_cols}컬럼  ({time.time()-t0:.1f}초)")

print("\n  GAP_TO_PAST1 분포:")
print(con.execute("""
  SELECT
    sum(CASE WHEN GAP_TO_PAST1 > 0 THEN 1 ELSE 0 END) AS past_real,
    sum(CASE WHEN GAP_TO_PAST1 < 0 THEN 1 ELSE 0 END) AS future_substitute,
    sum(CASE WHEN GAP_TO_PAST1 = 0 THEN 1 ELSE 0 END) AS zero_filled,
    median(GAP_TO_PAST1) AS median_gap
  FROM attack5_adjacent
""").df())

# ══════════════════════════════════════════════════════════════
# Step 6. 클래스 균형 언더샘플링
# ══════════════════════════════════════════════════════════════
print("\n[Step 6] 클래스별 언더샘플링")
t0 = time.time()
con.execute("DROP TABLE IF EXISTS attack5_sampled")
con.execute(f"""
CREATE TABLE attack5_sampled AS
SELECT * EXCLUDE (rn) FROM (
  SELECT *, row_number() OVER (PARTITION BY lower(Attack) ORDER BY random()) AS rn
  FROM attack5_adjacent
)
WHERE rn <= {SAMPLE_PER_CLASS}
""")
n_sampled = con.execute("SELECT count(*) FROM attack5_sampled").fetchone()[0]
print(f"  -> {n_sampled:,}행  ({time.time()-t0:.1f}초)")
print(con.execute("SELECT lower(Attack) AS attack, count(*) cnt FROM attack5_sampled GROUP BY 1 ORDER BY 2 DESC").df())

con.execute(f"COPY attack5_sampled TO '{OUT_SAMPLED_PATH}' (HEADER, DELIMITER ',')")
print(f"\n저장 완료: {OUT_SAMPLED_PATH}")

df = con.execute("SELECT * FROM attack5_sampled").df()

con.close()
os.remove(DB_PATH)

# ══════════════════════════════════════════════════════════════
# Step 5. 클리닝 (preprocess_01_cleaning.py 로직을 현재/과거1/과거2 3블록에 동일 적용)
# ══════════════════════════════════════════════════════════════
print("\n[Step 5] 클리닝 (컬럼 제거 / TCP_FLAGS 비트분해 / Z-score 정규화)")
print(f"  클리닝 전 shape: {df.shape}")

# 5-1. 중복/메타 피처 제거 (현재 블록은 IP주소도 포함해서 5개, 과거1/2는 IP없이 3개)
DROP_BASE = ['SRC_TO_DST_SECOND_BYTES', 'DST_TO_SRC_SECOND_BYTES', 'MAX_IP_PKT_LEN']
drop_cols = DROP_BASE + ['IPV4_SRC_ADDR', 'IPV4_DST_ADDR']  # 현재 블록
for prefix in ['past1_', 'past2_']:
    drop_cols += [f'{prefix}{c}' for c in DROP_BASE]
df.drop(columns=drop_cols, inplace=True)
print(f"  -> 컬럼 제거 ({len(drop_cols)}개): shape {df.shape}")

# 5-2. TCP_FLAGS 비트 분해 (현재/과거1/과거2 각 3개 컬럼 -> 8비트 x 9 = 72개)
FLAG_BASE = ['TCP_FLAGS', 'CLIENT_TCP_FLAGS', 'SERVER_TCP_FLAGS']
BIT_NAMES = ['FIN', 'SYN', 'RST', 'PSH', 'ACK', 'URG', 'ECE', 'CWR']
flag_cols = FLAG_BASE + [f'{p}{c}' for p in ['past1_', 'past2_'] for c in FLAG_BASE]
for col in flag_cols:
    vals = df[col].fillna(0).astype(float).to_numpy().astype(np.int64)
    for i, bit in enumerate(BIT_NAMES):
        df[f'{col}_{bit}'] = ((vals >> i) & 1).astype(np.uint8)
    df.drop(columns=[col], inplace=True)
print(f"  -> TCP_FLAGS 비트분해 ({len(flag_cols)}개 컬럼 -> {len(flag_cols)*8}개): shape {df.shape}")

# 5-3. Z-score 정규화 + ±3 클리핑 (Attack, 비트컬럼 제외)
EXCLUDE = ['Attack'] + [c for c in df.columns if any(f in c for f in FLAG_BASE)]
num_cols = [c for c in df.select_dtypes(include='number').columns if c not in EXCLUDE]
means = df[num_cols].mean()
stds = df[num_cols].std().replace(0, 1)
df[num_cols] = ((df[num_cols] - means) / stds).clip(-3, 3)
print(f"  -> Z-score 정규화 ({len(num_cols)}개 컬럼)")

# 5-4. Attack 레이블 인코딩 (5개 공격유형, 알파벳순)
df['Attack'] = df['Attack'].str.lower()
attack_classes = sorted(df['Attack'].unique())
attack_map = {v: i for i, v in enumerate(attack_classes)}
df['Attack_label'] = df['Attack'].map(attack_map)
print(f"  -> Attack_label 매핑: {attack_map}")

df.to_csv(OUT_CLEANED_PATH, index=False)
print(f"\n저장 완료: {OUT_CLEANED_PATH}  shape={df.shape}")

# ══════════════════════════════════════════════════════════════
# Step 7. Azure ML Designer 업로드용 최종 파일 (Attack 문자열 컬럼 제거)
# ══════════════════════════════════════════════════════════════
df_final = df.drop(columns=['Attack'])
df_final.to_csv(OUT_FINAL_PATH, index=False)
print(f"저장 완료: {OUT_FINAL_PATH}  shape={df_final.shape}")

_log_file.close()
sys.stdout = sys.__stdout__
print(f"로그 저장 완료: {LOG_PATH}")
