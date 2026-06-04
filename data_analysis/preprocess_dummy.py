"""
dummy_50000.csv 전처리 스크립트
preprocess_01_cleaning.py와 동일한 파이프라인 적용
추가: Date 컬럼 제거
출력: dummy_cleaned.csv, dummy_attack_only.csv, dummy_final.csv
"""

import numpy as np
import pandas as pd
import os, sys, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# ====== 경로 설정 ======
BASE       = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE, 'data', 'dummy_50000.csv')
FINAL_PATH = os.path.join(BASE, 'data', 'dummy_final.csv')

ROOT    = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

_ts      = datetime.now().strftime('%Y%m%d_%H%M')
LOG_PATH = os.path.join(LOG_DIR, f'preprocess_dummy_{_ts}.txt')

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
    'Dataset',
    'Date',                    # dummy 데이터 추가 컬럼
    'IPV4_SRC_ADDR',
    'IPV4_DST_ADDR',
    'SRC_TO_DST_SECOND_BYTES',
    'DST_TO_SRC_SECOND_BYTES',
    'MAX_IP_PKT_LEN',
]
DROP_COLS = [c for c in DROP_COLS if c in df.columns]
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
    if col in df.columns:
        n_over = (df[col] > CLIP_MAX).sum()
        df[col] = df[col].clip(upper=CLIP_MAX)
        print(f"  {col}: {n_over:,}개 클리핑")

# ══════════════════════════════════════════════════════════════
# Step 3. TCP_FLAGS 비트 분해
# ══════════════════════════════════════════════════════════════
FLAG_COLS = ['TCP_FLAGS', 'CLIENT_TCP_FLAGS', 'SERVER_TCP_FLAGS']
BIT_NAMES = ['FIN', 'SYN', 'RST', 'PSH', 'ACK', 'URG', 'ECE', 'CWR']

print(f"\n[Step 3] TCP_FLAGS 비트 분해")
for col in FLAG_COLS:
    if col in df.columns:
        for i, bit in enumerate(BIT_NAMES):
            vals = df[col].fillna(0).astype(float).to_numpy().astype(np.int64)
            df[f'{col}_{bit}'] = ((vals >> i) & 1).astype(np.uint8)
        df.drop(columns=[col], inplace=True)
        print(f"  {col} → {col}_FIN ~ {col}_CWR (8개 컬럼)")

print(f"  → shape: {df.shape}")

# ══════════════════════════════════════════════════════════════
# Step 4. Z-score 정규화 + ±3 클리핑
# ══════════════════════════════════════════════════════════════
EXCLUDE = (['Label', 'Attack']
           + [c for c in df.columns if any(f in c for f in FLAG_COLS)])
num_cols = [c for c in df.select_dtypes(include='number').columns if c not in EXCLUDE]

print(f"\n[Step 4] Z-score 정규화 + ±3 클리핑 ({len(num_cols)}개 컬럼)")
means = df[num_cols].mean()
stds  = df[num_cols].std().replace(0, 1)
df[num_cols] = ((df[num_cols] - means) / stds).clip(-3, 3)

clipped = (df[num_cols].abs() == 3).sum()
clipped = clipped[clipped > 0].sort_values(ascending=False)
print(f"  ±3으로 클리핑된 값이 있는 컬럼 ({len(clipped)}개):")
for col, cnt in clipped.items():
    print(f"    {col}: {cnt:,}개")

# ══════════════════════════════════════════════════════════════
# 저장 — final (분류 모델 추론용, 레이블 컬럼 전체 제거)
# ══════════════════════════════════════════════════════════════
drop_label_cols = [c for c in ['Attack', 'Label', 'Attack_label'] if c in df.columns]
df_final = df.drop(columns=drop_label_cols)
df_final.to_csv(FINAL_PATH, index=False)
print(f"\n[저장] final: {FINAL_PATH}  shape={df_final.shape}")
print(f"  제거된 레이블 컬럼: {drop_label_cols}")

_log_file.close()
sys.stdout = sys.__stdout__
print(f"\n로그 저장 완료: {LOG_PATH}")
