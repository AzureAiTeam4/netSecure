import os
from collections import Counter

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

# ── 파라미터 ──────────────────────────────────────────────────────────────────
CSV_FILE_NAME = "data/data/NF-UQ-NIDS-v2.csv"   # 샘플링데이터
CHUNK_SIZE = 500_000

ROOT = os.path.dirname(__file__)
CSV_PATH = os.path.join(ROOT, CSV_FILE_NAME)
csv_stem = os.path.splitext(os.path.basename(CSV_FILE_NAME))[0]
FIG_PATH = os.path.join(ROOT, "figures", f"distribution_{csv_stem}.png")

# ── 배치 카운트 ───────────────────────────────────────────────────────────────
label_counter = Counter()
attack_counter = Counter()

print(f"파일: {CSV_PATH}")
print("배치 처리 시작...")
for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE, usecols=["Label", "Attack"])):
    label_counter.update(chunk["Label"].astype(str).tolist())
    attack_counter.update(chunk["Attack"].tolist())
    if (i + 1) % 10 == 0:
        print(f"  {(i + 1) * CHUNK_SIZE:,}행 처리 완료")

print("\n처리 완료!\n")

# ── 결과 출력 ─────────────────────────────────────────────────────────────────
label_df = (
    pd.DataFrame(label_counter.items(), columns=["Label", "Count"])
    .assign(Label=lambda d: d["Label"].map({"0": "Benign", "1": "Attack"}))
    .sort_values("Count", ascending=False)
    .reset_index(drop=True)
)
attack_df = (
    pd.DataFrame(attack_counter.items(), columns=["Attack", "Count"])
    .sort_values("Count", ascending=False)
    .reset_index(drop=True)
)

total = label_df["Count"].sum()
print(f"=== Label 분포  (총 {total:,}행) ===")
for _, row in label_df.iterrows():
    print(f"  {row['Label']}: {row['Count']:,}  ({row['Count']/total*100:.2f}%)")

print("\n=== 공격 유형별 개수 ===")
for _, row in attack_df.iterrows():
    print(f"  {row['Attack']}: {row['Count']:,}  ({row['Count']/total*100:.2f}%)")

# ── 시각화 ────────────────────────────────────────────────────────────────────
label_counts = label_df.set_index("Label")["Count"]
attack_counts = attack_df.set_index("Attack")["Count"]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle(f"Distribution — {csv_stem}  (N={total:,})", fontsize=13, fontweight="bold")

ax1 = axes[0]
_, _, autotexts = ax1.pie(
    label_counts.values,
    labels=label_counts.index,
    autopct="%1.2f%%",
    colors=["#4CAF50", "#F44336"],
    startangle=90,
    textprops={"fontsize": 12},
)
for at in autotexts:
    at.set_fontsize(11)
ax1.set_title("Label Distribution (Benign vs Attack)", fontsize=12)

ax2 = axes[1]
top = attack_counts[attack_counts.index != "Benign"].head(20)
bars = ax2.barh(top.index[::-1], top.values[::-1], color="#2196F3")
ax2.set_xlabel("Count", fontsize=11)
ax2.set_title("Attack Type Distribution (Top 20, excl. Benign)", fontsize=12)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar, cnt in zip(bars, top.values[::-1]):
    ax2.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
             f"{cnt:,}", va="center", fontsize=8)

plt.tight_layout()
plt.savefig(FIG_PATH, dpi=150, bbox_inches="tight")
print(f"\n그래프 저장: {FIG_PATH}")
plt.show()
