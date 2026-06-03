import numpy as np
import pandas as pd
import os, sys, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# ====== 경로 설정 ======
DATA_PATH = 'data/data/sampled_dataset.csv'
OUT_PATH  = 'data/data/cleaned_dataset.csv'

ROOT    = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# ====== 로그 세팅 ======
_script  = os.path.splitext(os.path.basename(__file__))[0]
_ts      = datetime.now().strftime('%Y%m%d_%H%M')
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
print(f"로그 저장: {LOG_PATH}\n")

# ====== 데이터 로드 ======
df = pd.read_csv(DATA_PATH)
print(f"로드 완료 - shape: {df.shape}")

# ══════════════════════════════════════════════════════════════
# Step 1. 불필요 feature 제거
# ══════════════════════════════════════════════════════════════
DROP_COLS = [
    'Dataset',              # 수집 환경 메타정보
    'IPV4_SRC_ADDR',        # 실험용 IP
    'IPV4_DST_ADDR',        # 실험용 IP
    'SRC_TO_DST_SECOND_BYTES',  # AVG_THROUGHPUT의 파생, 극단값 심각
    'DST_TO_SRC_SECOND_BYTES',  # AVG_THROUGHPUT의 파생, 극단값 심각
    'MAX_IP_PKT_LEN',       # LONGEST_FLOW_PKT와 완전 동일
]
df.drop(columns=DROP_COLS, inplace=True)
print(f"\n[Step 1] 컬럼 제거 완료 ({len(DROP_COLS)}개): {DROP_COLS}")
print(f"  → shape: {df.shape}")

# ══════════════════════════════════════════════════════════════
# Step 2. AVG_THROUGHPUT 클리핑 (1.0e+9)
# ══════════════════════════════════════════════════════════════
CLIP_COLS = ['SRC_TO_DST_AVG_THROUGHPUT', 'DST_TO_SRC_AVG_THROUGHPUT']
CLIP_MAX  = 1.0e+9

print(f"\n[Step 2] AVG_THROUGHPUT 클리핑 (>{CLIP_MAX:.0e} → {CLIP_MAX:.0e})")
for col in CLIP_COLS:
    n_over = (df[col] > CLIP_MAX).sum()
    df[col] = df[col].clip(upper=CLIP_MAX)
    print(f"  {col}: {n_over:,}개 클리핑")

# ══════════════════════════════════════════════════════════════
# Step 3. TCP_FLAGS 비트 분해
# ══════════════════════════════════════════════════════════════
FLAG_COLS = ['TCP_FLAGS', 'CLIENT_TCP_FLAGS', 'SERVER_TCP_FLAGS']
BIT_NAMES = ['FIN', 'SYN', 'RST', 'PSH', 'ACK', 'URG', 'ECE', 'CWR']  # bit0~7

print(f"\n[Step 3] TCP_FLAGS 비트 분해")
for col in FLAG_COLS:
    for i, bit in enumerate(BIT_NAMES):
        vals = df[col].fillna(0).astype(float).to_numpy().astype(np.int64)
        df[f'{col}_{bit}'] = ((vals >> i) & 1).astype(np.uint8)
    df.drop(columns=[col], inplace=True)
    print(f"  {col} → {col}_FIN ~ {col}_CWR (8개 컬럼)")

print(f"  → shape: {df.shape}")

# ══════════════════════════════════════════════════════════════
# Step 4. Z-score 정규화 + ±3 클리핑
# ══════════════════════════════════════════════════════════════
# Label, Attack, TCP 비트 컬럼은 제외
EXCLUDE = (['Label', 'Attack']
           + [c for c in df.columns if any(f in c for f in FLAG_COLS)])
num_cols = [c for c in df.select_dtypes(include='number').columns if c not in EXCLUDE]

print(f"\n[Step 4] Z-score 정규화 + ±3 클리핑 ({len(num_cols)}개 컬럼)")
means = df[num_cols].mean()
stds  = df[num_cols].std().replace(0, 1)   # std=0인 컬럼 division by zero 방지
df[num_cols] = ((df[num_cols] - means) / stds).clip(-3, 3)

clipped = (df[num_cols].abs() == 3).sum()
clipped = clipped[clipped > 0].sort_values(ascending=False)
print(f"  ±3으로 클리핑된 값이 있는 컬럼 ({len(clipped)}개):")
for col, cnt in clipped.items():
    print(f"    {col}: {cnt:,}개")

# ══════════════════════════════════════════════════════════════
# Step 5. Attack 레이블 전처리
# ══════════════════════════════════════════════════════════════
print(f"\n[Step 5] Attack 레이블 전처리")

# 소문자 통일
df['Attack'] = df['Attack'].str.lower()
print(f"  소문자 통일 완료")
print(f"  고유값: {sorted(df['Attack'].unique())}")

# 정수 매핑 (benign=0, 공격 유형 알파벳순)
attack_classes = sorted(df['Attack'].unique())
attack_map = {v: i for i, v in enumerate(attack_classes)}
df['Attack_label'] = df['Attack'].map(attack_map)
print(f"  정수 매핑:")
for k, v in attack_map.items():
    print(f"    {v}: {k}")

# ══════════════════════════════════════════════════════════════
# 저장
# ══════════════════════════════════════════════════════════════
df.to_csv(OUT_PATH, index=False)
print(f"\n저장 완료: {OUT_PATH}")
print(f"최종 shape: {df.shape}")
print(f"최종 컬럼: {df.columns.tolist()}")

_log_file.close()
sys.stdout = sys.__stdout__
print(f"로그 저장 완료: {LOG_PATH}")