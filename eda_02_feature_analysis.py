import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os, sys, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# ====== 경로 설정 ======
DATA_PATH = 'data/sampled_dataset.csv'

ROOT    = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(ROOT, 'figures')
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# ====== 로그 세팅 (stdout → 콘솔 + txt 동시 저장) ======
_script = os.path.splitext(os.path.basename(__file__))[0]
_ts     = datetime.now().strftime('%Y%m%d_%H%M')
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

# ===== raw 데이터 확인 (칼럼 분포) =====

print("=" * 60)
print(f"shape : {df.shape}")
print("=" * 60)

# ── 칼럼 타입 분리
num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = df.select_dtypes(exclude='number').columns.tolist()
print(f"수치형 칼럼 ({len(num_cols)}개): {num_cols}")
print(f"범주형 칼럼 ({len(cat_cols)}개): {cat_cols}")

# ── 결측값
print("\n=== 결측값 ===")
null_df = df.isnull().sum().rename('null_count')
null_df = null_df[null_df > 0]
if null_df.empty:
    print("  결측값 없음")
else:
    null_df['null_pct'] = (null_df / len(df) * 100).round(2)
    print(null_df.to_string())

# ── 수치형 기술통계
print("\n=== 수치형 칼럼 기술통계 ===")
print(df[num_cols].describe().T.to_string())

# ── 범주형 분포 (고유값 20개 초과 시 상위 10개만 출력)
TOP_N = 10
UNIQUE_THRESH = 20

print("\n=== 범주형 칼럼 분포 ===")
for col in cat_cols:
    vc = df[col].value_counts()
    nunique = len(vc)
    print(f"\n  [{col}]  (고유값 {nunique:,}개)")
    if nunique > UNIQUE_THRESH:
        print(f"  → 고유값이 많아 상위 {TOP_N}개만 출력")
        vc = vc.head(TOP_N)
    for val, cnt in vc.items():
        print(f"    {val}: {cnt:,}  ({cnt/len(df)*100:.2f}%)")

# ── 수치형 칼럼 분포 시각화 (히스토그램)
n_cols = 5
n_rows = (len(num_cols) + n_cols - 1) // n_cols
fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 3))
axes = axes.flatten()

for i, col in enumerate(num_cols):
    axes[i].hist(df[col].dropna(), bins=50, color='#2196F3', edgecolor='none')
    axes[i].set_title(col, fontsize=9)
    axes[i].set_ylabel('count')
    axes[i].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    axes[i].tick_params(axis='x', labelsize=7, rotation=30)

for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.suptitle('Numeric Column Distributions', fontsize=13, fontweight='bold')
plt.tight_layout()
fig_path = os.path.join(FIG_DIR, 'numeric_distributions.png')
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
print(f"\n그래프 저장: {fig_path}")
plt.show()
