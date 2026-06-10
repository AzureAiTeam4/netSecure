"""
attack_only_dataset.csv (60만개/class, 55컬럼)의 20만개/class 버전 생성

기존 파이프라인(sampling.ipynb -> preprocess_01_cleaning.py -> prepare_attack_data.py)과
동일한 55컬럼 feature set을, 원본 NF-UQ-NIDS-v2.csv에서 직접 20만개/class로 재추출.

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
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

RAW_PATH = os.path.join(DATA_DIR, 'NF-UQ-NIDS-v2.csv')
DB_PATH = os.path.join(DATA_DIR, 'baseline_pipeline.duckdb')
OUT_PATH = os.path.join(DATA_DIR, 'attack_only_200k.csv')

TARGET_CLASSES = ['scanning', 'reconnaissance', 'xss', 'password', 'injection']
SAMPLE_PER_CLASS = 200_000

# attack_only_dataset.csv와 동일한 32개 feature 컬럼
# (원본 46 - sampling.ipynb에서 drop한 6개 - preprocess_01에서 drop한 6개 - Label/Attack/Dataset)
FEATURE_COLS = [
    'L4_SRC_PORT', 'L4_DST_PORT', 'PROTOCOL', 'L7_PROTO', 'IN_BYTES', 'IN_PKTS', 'OUT_BYTES', 'OUT_PKTS',
    'TCP_FLAGS', 'CLIENT_TCP_FLAGS', 'SERVER_TCP_FLAGS',
    'FLOW_DURATION_MILLISECONDS', 'DURATION_IN', 'DURATION_OUT', 'MIN_TTL', 'MAX_TTL',
    'LONGEST_FLOW_PKT', 'SHORTEST_FLOW_PKT', 'MIN_IP_PKT_LEN',
    'RETRANSMITTED_IN_BYTES', 'RETRANSMITTED_IN_PKTS', 'RETRANSMITTED_OUT_BYTES', 'RETRANSMITTED_OUT_PKTS',
    'SRC_TO_DST_AVG_THROUGHPUT', 'DST_TO_SRC_AVG_THROUGHPUT',
    'NUM_PKTS_UP_TO_128_BYTES', 'NUM_PKTS_128_TO_256_BYTES', 'NUM_PKTS_256_TO_512_BYTES',
    'NUM_PKTS_512_TO_1024_BYTES', 'NUM_PKTS_1024_TO_1514_BYTES',
    'TCP_WIN_MAX_IN', 'TCP_WIN_MAX_OUT',
]
assert len(FEATURE_COLS) == 32

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
print(f"RAW_PATH={RAW_PATH}\n")

# ══════════════════════════════════════════════════════════════
# Step 1. 5종 공격 필터 + 클래스별 20만개 언더샘플링 (DuckDB)
# ══════════════════════════════════════════════════════════════
print("[Step 1] 5종 공격 필터 + 클래스별 20만개 언더샘플링")
t0 = time.time()

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
con = duckdb.connect(DB_PATH)
con.execute("PRAGMA memory_limit='10GB'")

target_list = ", ".join(f"'{c}'" for c in TARGET_CLASSES)

con.execute(f"""
CREATE TABLE attack5_sampled AS
SELECT * EXCLUDE (rn) FROM (
  SELECT {', '.join(FEATURE_COLS)}, Attack,
         row_number() OVER (PARTITION BY lower(Attack) ORDER BY random()) AS rn
  FROM read_csv_auto('{RAW_PATH}')
  WHERE lower(Attack) IN ({target_list})
)
WHERE rn <= {SAMPLE_PER_CLASS}
""")

n_sampled = con.execute("SELECT count(*) FROM attack5_sampled").fetchone()[0]
print(f"  -> {n_sampled:,}행  ({time.time()-t0:.1f}초)")
print(con.execute("SELECT lower(Attack) AS attack, count(*) cnt FROM attack5_sampled GROUP BY 1 ORDER BY 2 DESC").df())

df = con.execute("SELECT * FROM attack5_sampled").df()
con.close()
os.remove(DB_PATH)

# ══════════════════════════════════════════════════════════════
# Step 2. AVG_THROUGHPUT 클리핑 (1.0e+9)
# ══════════════════════════════════════════════════════════════
CLIP_COLS = ['SRC_TO_DST_AVG_THROUGHPUT', 'DST_TO_SRC_AVG_THROUGHPUT']
CLIP_MAX = 1.0e+9
print(f"\n[Step 2] AVG_THROUGHPUT 클리핑 (>{CLIP_MAX:.0e} -> {CLIP_MAX:.0e})")
for col in CLIP_COLS:
    n_over = (df[col] > CLIP_MAX).sum()
    df[col] = df[col].clip(upper=CLIP_MAX)
    print(f"  {col}: {n_over:,}개 클리핑")

# ══════════════════════════════════════════════════════════════
# Step 3. TCP_FLAGS 비트 분해 (3개 컬럼 -> 24개)
# ══════════════════════════════════════════════════════════════
FLAG_COLS = ['TCP_FLAGS', 'CLIENT_TCP_FLAGS', 'SERVER_TCP_FLAGS']
BIT_NAMES = ['FIN', 'SYN', 'RST', 'PSH', 'ACK', 'URG', 'ECE', 'CWR']
print(f"\n[Step 3] TCP_FLAGS 비트 분해")
for col in FLAG_COLS:
    vals = df[col].fillna(0).astype(float).to_numpy().astype(np.int64)
    for i, bit in enumerate(BIT_NAMES):
        df[f'{col}_{bit}'] = ((vals >> i) & 1).astype(np.uint8)
    df.drop(columns=[col], inplace=True)
    print(f"  {col} -> {col}_FIN ~ {col}_CWR (8개 컬럼)")
print(f"  -> shape: {df.shape}")

# ══════════════════════════════════════════════════════════════
# Step 4. Z-score 정규화 + ±3 클리핑
# ══════════════════════════════════════════════════════════════
EXCLUDE = ['Attack'] + [c for c in df.columns if any(f in c for f in FLAG_COLS)]
num_cols = [c for c in df.select_dtypes(include='number').columns if c not in EXCLUDE]
print(f"\n[Step 4] Z-score 정규화 + ±3 클리핑 ({len(num_cols)}개 컬럼)")
means = df[num_cols].mean()
stds = df[num_cols].std().replace(0, 1)
df[num_cols] = ((df[num_cols] - means) / stds).clip(-3, 3)

# ══════════════════════════════════════════════════════════════
# Step 5. Attack_label 인코딩 (5개 공격유형, 알파벳순 0~4 -- adjacent_final.csv와 동일 매핑)
# ══════════════════════════════════════════════════════════════
df['Attack'] = df['Attack'].str.lower()
attack_classes = sorted(df['Attack'].unique())
attack_map = {v: i for i, v in enumerate(attack_classes)}
df['Attack_label'] = df['Attack'].map(attack_map)
print(f"\n[Step 5] Attack_label 매핑: {attack_map}")

# ══════════════════════════════════════════════════════════════
# 저장
# ══════════════════════════════════════════════════════════════
df.to_csv(OUT_PATH, index=False)
print(f"\n저장 완료: {OUT_PATH}  shape={df.shape}")
print(f"컬럼: {df.columns.tolist()}")

_log_file.close()
sys.stdout = sys.__stdout__
print(f"로그 저장 완료: {LOG_PATH}")
