"""
정규화로 인해 패턴이 불분명한 컬럼을 원본값(sampled_dataset.csv)으로 재분석

대상 피처 (정규화된 분석에서 패턴이 미미했던 것들):
  IN_BYTES, OUT_BYTES
  IN_PKTS, OUT_PKTS
  NUM_PKTS_UP_TO_128_BYTES, NUM_PKTS_1024_TO_1514_BYTES
  RETRANSMITTED_OUT_PKTS, RETRANSMITTED_IN_PKTS

데이터: sampled_dataset.csv (raw값, Benign 포함)
  → Benign 제외 후 공격 5종만 분석
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

DATA_PATH  = "data/data/sampled_dataset.csv"
OUTPUT_DIR = Path("data/analysis_results/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_FEATURES = [
    "IN_BYTES", "OUT_BYTES",
    "IN_PKTS", "OUT_PKTS",
    "NUM_PKTS_UP_TO_128_BYTES",
    "NUM_PKTS_1024_TO_1514_BYTES",
    "RETRANSMITTED_OUT_PKTS",
    "RETRANSMITTED_IN_PKTS",
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
# 데이터 로드 (공격 행만)
# ──────────────────────────────────────────────
print("데이터 로딩 중 (sampled_dataset.csv)...")
use_cols = RAW_FEATURES + ["Attack"]
df = pd.read_csv(DATA_PATH, usecols=use_cols)

df["Attack"] = df["Attack"].str.lower()
df = df[df["Attack"] != "benign"].copy()

print(f"공격 행 로드 완료: {df.shape[0]:,} rows")
print(df["Attack"].value_counts(), "\n")


# ──────────────────────────────────────────────
# 1. 기술통계 (원본값)
# ──────────────────────────────────────────────
print("=" * 65)
print("1. 기술통계 (원본값)")

stats_records = []
for feat in RAW_FEATURES:
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        q = grp.quantile([0.25, 0.50, 0.75, 0.90, 0.95])
        stats_records.append({
            "feature": feat,
            "attack":  attack,
            "count":   len(grp),
            "mean":    grp.mean(),
            "median":  q[0.50],
            "std":     grp.std(),
            "min":     grp.min(),
            "q25":     q[0.25],
            "q75":     q[0.75],
            "q90":     q[0.90],
            "q95":     q[0.95],
            "max":     grp.max(),
        })

stats_df = pd.DataFrame(stats_records)

for feat in RAW_FEATURES:
    sub = stats_df[stats_df["feature"] == feat].set_index("attack")
    cols = ["mean", "median", "std", "q25", "q75", "q90", "q95", "max"]
    print(f"\n── {feat} (raw) ──")
    print(sub[cols].round(2).to_string())


# ──────────────────────────────────────────────
# 2. 공격 간 중앙값 비교 (전체 중앙값 대비 비율)
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("2. 전체 중앙값 대비 공격별 중앙값 비율")

overall_median = df[RAW_FEATURES].median()
ratio_records = []

for feat in RAW_FEATURES:
    overall_med = overall_median[feat]
    row = {"feature": feat, "overall_median": overall_med}
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        atk_med = grp.median()
        ratio = (atk_med / overall_med) if overall_med != 0 else np.nan
        row[f"{attack}_median"] = atk_med
        row[f"{attack}_ratio"]  = round(ratio, 4) if not np.isnan(ratio) else np.nan
    ratio_records.append(row)

ratio_df = pd.DataFrame(ratio_records)

print("\n[중앙값 (raw)]")
med_cols = ["feature", "overall_median"] + [f"{a}_median" for a in ATTACK_ORDER]
print(ratio_df[med_cols].to_string(index=False))

print("\n[전체 중앙값 대비 비율]")
ratio_cols = ["feature"] + [f"{a}_ratio" for a in ATTACK_ORDER]
print(ratio_df[ratio_cols].to_string(index=False))


# ──────────────────────────────────────────────
# 3. 이상치 비율
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("3. 이상치 비율")

outlier_records = []
for feat in RAW_FEATURES:
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        n = len(grp)

        q1, q3 = grp.quantile(0.25), grp.quantile(0.75)
        iqr = q3 - q1
        iqr_out = ((grp < q1 - 1.5 * iqr) | (grp > q3 + 1.5 * iqr)).sum()

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

for feat in RAW_FEATURES:
    sub = outlier_df[outlier_df["feature"] == feat].set_index("attack")
    cols = ["iqr_outlier_pct", "z2_outlier_pct", "z3_outlier_pct"]
    print(f"\n── {feat} 이상치 비율(%) ──")
    print(sub[cols].to_string())


# ──────────────────────────────────────────────
# 4. 시각화 (박스플롯 + 히스토그램)
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("4. 시각화 생성 중...")

SAMPLE_SIZE = 50_000
sample_parts = []
for attack in ATTACK_ORDER:
    grp = df[df["Attack"] == attack]
    if len(grp) > SAMPLE_SIZE:
        grp = grp.sample(SAMPLE_SIZE, random_state=42)
    sample_parts.append(grp)
df_sample = pd.concat(sample_parts, ignore_index=True)

for feat in RAW_FEATURES:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"{feat}  (raw values, n≤{SAMPLE_SIZE:,}/attack)", fontsize=12)

    # 박스플롯 (이상치 제외)
    ax1 = axes[0]
    data_list, labels = [], []
    for attack in ATTACK_ORDER:
        vals = df_sample.loc[df_sample["Attack"] == attack, feat].dropna()
        data_list.append(vals.values)
        labels.append(attack)

    bp = ax1.boxplot(
        data_list, labels=labels,
        showfliers=False, patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
    )
    for patch, attack in zip(bp["boxes"], ATTACK_ORDER):
        patch.set_facecolor(COLORS[attack])
        patch.set_alpha(0.7)

    ax1.set_title("Boxplot (no outliers)")
    ax1.set_xlabel("Attack Type")
    ax1.set_ylabel(f"{feat} (raw)")
    ax1.tick_params(axis='x', rotation=15)

    all_vals = df_sample[feat].dropna()
    if all_vals.min() > 0:
        ax1.set_yscale("log")

    # 히스토그램 (99% quantile 이내로 x축 클리핑해서 가독성 확보)
    ax2 = axes[1]
    clip_max = df_sample[feat].quantile(0.99)
    for attack in ATTACK_ORDER:
        vals = df_sample.loc[df_sample["Attack"] == attack, feat].dropna()
        vals_clipped = vals[vals <= clip_max]
        ax2.hist(vals_clipped, bins=60, alpha=0.45,
                 label=attack, color=COLORS[attack], density=True)

    ax2.set_title(f"Histogram (density, x≤{clip_max:.0f})")
    ax2.set_xlabel(f"{feat} (raw)")
    ax2.set_ylabel("Density")
    ax2.legend(fontsize=8)

    plt.tight_layout()
    out_path = OUTPUT_DIR / f"raw_{feat}.png"
    plt.savefig(out_path, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"  저장: {out_path}")


# ──────────────────────────────────────────────
# 5. 위험도 계산식용 임계값 요약
#    각 피처별 공격 유형 90%, 95% 분위수 요약
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("5. 위험도 임계값 설정 참고 (공격 유형별 분위수)")

threshold_records = []
for feat in RAW_FEATURES:
    row = {"feature": feat}
    for attack in ATTACK_ORDER:
        grp = df.loc[df["Attack"] == attack, feat].dropna()
        row[f"{attack}_q50"] = round(grp.quantile(0.50), 2)
        row[f"{attack}_q90"] = round(grp.quantile(0.90), 2)
        row[f"{attack}_q95"] = round(grp.quantile(0.95), 2)
    threshold_records.append(row)

thresh_df = pd.DataFrame(threshold_records)

for attack in ATTACK_ORDER:
    cols = ["feature", f"{attack}_q50", f"{attack}_q90", f"{attack}_q95"]
    print(f"\n[{attack}]")
    print(thresh_df[cols].rename(columns={
        f"{attack}_q50": "q50(중앙값)",
        f"{attack}_q90": "q90",
        f"{attack}_q95": "q95",
    }).to_string(index=False))


# ──────────────────────────────────────────────
# 6. CSV 저장
# ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("6. CSV 저장 중...")

stats_df.to_csv(OUTPUT_DIR / "raw_descriptive_stats.csv", index=False)
ratio_df.to_csv(OUTPUT_DIR / "raw_median_ratio.csv", index=False)
outlier_df.to_csv(OUTPUT_DIR / "raw_outlier_ratio.csv", index=False)
thresh_df.to_csv(OUTPUT_DIR / "raw_threshold_reference.csv", index=False)

print(f"  저장 위치: {OUTPUT_DIR}/")
print("  - raw_descriptive_stats.csv")
print("  - raw_median_ratio.csv")
print("  - raw_outlier_ratio.csv")
print("  - raw_threshold_reference.csv")
print("\n완료.")
