"""
attack_only_dataset.csv 피처 분포 분석
- 정규화된 데이터 기준 (z-score normalized)
- 공격 유형 5종: reconnaissance, scanning, injection, xss, password
- Benign 없음 → 공격 간 비교(각 공격 vs 전체 중앙값)로 대체
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

DATA_PATH = "data/data/attack_only_dataset.csv"
OUTPUT_DIR = Path("data/analysis_results")
OUTPUT_DIR.mkdir(exist_ok=True)

FEATURES = [
    "IN_BYTES", "OUT_BYTES",
    "IN_PKTS", "OUT_PKTS",
    "FLOW_DURATION_MILLISECONDS",
    "RETRANSMITTED_OUT_PKTS", "RETRANSMITTED_IN_PKTS",
    "MIN_TTL", "MAX_TTL",
    "NUM_PKTS_UP_TO_128_BYTES",
    "NUM_PKTS_1024_TO_1514_BYTES",
    "TCP_FLAGS_SYN", "TCP_FLAGS_ACK",
    "TCP_FLAGS_RST", "TCP_FLAGS_FIN",
    "L4_DST_PORT",
]

ATTACK_ORDER = ["reconnaissance", "scanning", "injection", "xss", "password"]
COLORS = {
    "reconnaissance": "#e41a1c",
    "scanning":       "#377eb8",
    "injection":      "#4daf4a",
    "xss":            "#ff7f00",
    "password":       "#984ea3",
}


# ──────────────────────────────────────────────
# 데이터 로드 (필요 컬럼만)
# ──────────────────────────────────────────────
print("데이터 로딩 중...")
use_cols = FEATURES + ["Attack"]
df = pd.read_csv(DATA_PATH, usecols=use_cols)

# 컬럼 유효성 확인
missing = [f for f in FEATURES if f not in df.columns]
if missing:
    print(f"[WARNING] 없는 컬럼: {missing}")
    FEATURES = [f for f in FEATURES if f in df.columns]

print(f"로드 완료: {df.shape[0]:,} rows × {df.shape[1]} cols")
print("공격 분포:\n", df["Attack"].value_counts(), "\n")


# ──────────────────────────────────────────────
# 1. 기술통계 (공격 유형별)
# ──────────────────────────────────────────────
print("=" * 60)
print("1. 기술통계 계산 중...")

stats_records = []

for feat in FEATURES:
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        q = grp.quantile([0.25, 0.75, 0.90, 0.95])
        stats_records.append({
            "feature":  feat,
            "attack":   attack,
            "count":    len(grp),
            "mean":     grp.mean(),
            "median":   grp.median(),
            "std":      grp.std(),
            "min":      grp.min(),
            "q25":      q[0.25],
            "q75":      q[0.75],
            "q90":      q[0.90],
            "q95":      q[0.95],
            "max":      grp.max(),
        })

stats_df = pd.DataFrame(stats_records)

# 콘솔 출력 (피처별로)
for feat in FEATURES:
    sub = stats_df[stats_df["feature"] == feat].set_index("attack")
    cols = ["mean", "median", "std", "q25", "q75", "q90", "q95", "max"]
    print(f"\n── {feat} ──")
    print(sub[cols].round(4).to_string())


# ──────────────────────────────────────────────
# 2. 공격 간 중앙값 비교
#    (전체 중앙값 대비 각 공격의 중앙값 비율)
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. 전체 중앙값 대비 공격별 중앙값 비율 (공격 중앙값 / 전체 중앙값)")

overall_median = df[FEATURES].median()

ratio_records = []
for feat in FEATURES:
    overall_med = overall_median[feat]
    row = {"feature": feat, "overall_median": round(overall_med, 6)}
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        atk_med = grp.median()
        ratio = (atk_med / overall_med) if overall_med != 0 else np.nan
        row[f"{attack}_median"] = round(atk_med, 6)
        row[f"{attack}_ratio"]  = round(ratio, 4)
    ratio_records.append(row)

ratio_df = pd.DataFrame(ratio_records)

print("\n[중앙값]")
median_cols = ["feature", "overall_median"] + [f"{a}_median" for a in ATTACK_ORDER]
print(ratio_df[median_cols].to_string(index=False))

print("\n[전체 중앙값 대비 비율]")
ratio_cols = ["feature"] + [f"{a}_ratio" for a in ATTACK_ORDER]
print(ratio_df[ratio_cols].to_string(index=False))


# ──────────────────────────────────────────────
# 3. 이상치 비율 (IQR, Z-score 2σ, Z-score 3σ)
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. 이상치 비율 계산 중...")

outlier_records = []

for feat in FEATURES:
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        n = len(grp)

        # IQR 기준
        q1, q3 = grp.quantile(0.25), grp.quantile(0.75)
        iqr = q3 - q1
        iqr_out = ((grp < q1 - 1.5 * iqr) | (grp > q3 + 1.5 * iqr)).sum()

        # Z-score 기준
        mean, std = grp.mean(), grp.std()
        if std > 0:
            z = (grp - mean) / std
            z2_out = (z.abs() > 2).sum()
            z3_out = (z.abs() > 3).sum()
        else:
            z2_out = z3_out = 0

        outlier_records.append({
            "feature":         feat,
            "attack":          attack,
            "n":               n,
            "iqr_outlier_pct": round(iqr_out / n * 100, 2),
            "z2_outlier_pct":  round(z2_out / n * 100, 2),
            "z3_outlier_pct":  round(z3_out / n * 100, 2),
        })

outlier_df = pd.DataFrame(outlier_records)

for feat in FEATURES:
    sub = outlier_df[outlier_df["feature"] == feat].set_index("attack")
    cols = ["iqr_outlier_pct", "z2_outlier_pct", "z3_outlier_pct"]
    print(f"\n── {feat} 이상치 비율(%) ──")
    print(sub[cols].to_string())


# ──────────────────────────────────────────────
# 4. 시각화 (박스플롯 + 히스토그램)
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. 시각화 생성 중...")

# 메모리 절약을 위해 시각화용 샘플 (공격당 최대 50,000개)
SAMPLE_SIZE = 50_000
sample_parts = []
for attack in ATTACK_ORDER:
    grp = df[df["Attack"] == attack]
    if len(grp) > SAMPLE_SIZE:
        grp = grp.sample(SAMPLE_SIZE, random_state=42)
    sample_parts.append(grp)
df_sample = pd.concat(sample_parts, ignore_index=True)

for feat in FEATURES:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"{feat}  (normalized values, n≤{SAMPLE_SIZE:,}/attack)", fontsize=12)

    # ── 박스플롯 (이상치 제외, y축 로그 스케일) ──
    ax1 = axes[0]
    data_list = []
    labels = []
    for attack in ATTACK_ORDER:
        vals = df_sample.loc[df_sample["Attack"] == attack, feat].dropna()
        data_list.append(vals.values)
        labels.append(attack)

    bp = ax1.boxplot(
        data_list,
        labels=labels,
        showfliers=False,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
    )
    for patch, attack in zip(bp["boxes"], ATTACK_ORDER):
        patch.set_facecolor(COLORS[attack])
        patch.set_alpha(0.7)

    ax1.set_title("Boxplot (no outliers)")
    ax1.set_xlabel("Attack Type")
    ax1.set_ylabel(f"{feat} (normalized)")
    ax1.tick_params(axis='x', rotation=15)

    # y축: 값이 양수 영역만 있을 때만 로그 스케일 적용
    all_vals = df_sample[feat].dropna()
    if all_vals.min() > 0:
        ax1.set_yscale("log")

    # ── 히스토그램 겹쳐 그리기 ──
    ax2 = axes[1]
    for attack in ATTACK_ORDER:
        vals = df_sample.loc[df_sample["Attack"] == attack, feat].dropna()
        ax2.hist(
            vals,
            bins=50,
            alpha=0.45,
            label=attack,
            color=COLORS[attack],
            density=True,
        )
    ax2.set_title("Histogram (density)")
    ax2.set_xlabel(f"{feat} (normalized)")
    ax2.set_ylabel("Density")
    ax2.legend(fontsize=8)

    plt.tight_layout()
    out_path = OUTPUT_DIR / f"dist_{feat}.png"
    plt.savefig(out_path, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"  저장: {out_path}")


# ──────────────────────────────────────────────
# 5. CSV 저장
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("5. 결과 CSV 저장 중...")

# 기술통계
stats_out = OUTPUT_DIR / "descriptive_stats.csv"
stats_df.to_csv(stats_out, index=False)
print(f"  기술통계: {stats_out}")

# 중앙값 비율
ratio_out = OUTPUT_DIR / "median_ratio.csv"
ratio_df.to_csv(ratio_out, index=False)
print(f"  중앙값 비율: {ratio_out}")

# 이상치 비율
outlier_out = OUTPUT_DIR / "outlier_ratio.csv"
outlier_df.to_csv(outlier_out, index=False)
print(f"  이상치 비율: {outlier_out}")

# 통합 (distribution_analysis.csv)
merged = stats_df.merge(outlier_df, on=["feature", "attack"])
combined_out = Path("data/distribution_analysis.csv")
merged.to_csv(combined_out, index=False)
print(f"  통합 결과: {combined_out}")

print("\n완료.")
