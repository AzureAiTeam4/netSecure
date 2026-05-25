import pandas as pd
import numpy as np
import os
from datetime import datetime
from utils import plot_distribution

CSV_PATH = os.path.join(os.path.dirname(__file__), "NF-UQ-NIDS-v2.csv")
TARGET_N = 100_000
CHUNK_SIZE = 500_000
SEED = 42

# 소수 그룹 처리 전략:
# "drop"  → 샘플링 후 MIN_GROUP_SIZE 미만인 Attack 유형 제거 후 비율 재계산
# "keep"  → 모두 유지 (이후 SMOTE 등으로 처리 예정)
MINORITY_STRATEGY = "keep"
MIN_GROUP_SIZE = 50

_ts = datetime.now().strftime("%Y%m%d_%H%M")
_tag = f"{TARGET_N // 1000}k_{MINORITY_STRATEGY}_min{MIN_GROUP_SIZE}_{_ts}"
_root = os.path.dirname(__file__)
OUT_PATH = os.path.join(_root, "data", f"sampled_{_tag}.csv")
FIG_PATH = os.path.join(_root, "figures", f"undersampled_{_tag}.png")

rng = np.random.default_rng(SEED)

# ── Step 1: Attack 유형별 전체 개수 파악 ─────────────────────────────────────
print("Step 1: 전체 행 수 카운트 중...")
total_rows = 0
attack_total = {}

for chunk in pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE, usecols=["Attack"]):
    total_rows += len(chunk)
    for atk, cnt in chunk["Attack"].value_counts().items():
        attack_total[atk] = attack_total.get(atk, 0) + cnt

print(f"  총 행 수: {total_rows:,}  /  Attack 유형 수: {len(attack_total)}")

# ── Step 2: 소수 그룹 결정 ───────────────────────────────────────────────────
preview_targets = {atk: round(TARGET_N * cnt / total_rows)
                   for atk, cnt in attack_total.items()}

if MINORITY_STRATEGY == "drop":
    dropped = {atk for atk, n in preview_targets.items() if n < MIN_GROUP_SIZE}
    print(f"\n[DROP] 샘플 {MIN_GROUP_SIZE}개 미만 → 제거 ({len(dropped)}개):")
    for atk in sorted(dropped):
        print(f"  - {atk}: 원본 {attack_total[atk]:,}개, 예상 샘플 {preview_targets[atk]}개")
    active = {k: v for k, v in attack_total.items() if k not in dropped}
else:
    dropped = set()
    active = attack_total

total_active = sum(active.values())

# 비율 재계산 및 반올림 오차 보정
sample_targets = {atk: round(TARGET_N * cnt / total_active) for atk, cnt in active.items()}
dominant = max(active, key=active.get)
sample_targets[dominant] += TARGET_N - sum(sample_targets.values())

print(f"\nStep 2: 유형별 샘플 목표 (총 {sum(sample_targets.values()):,})")
for atk, n in sorted(sample_targets.items(), key=lambda x: -x[1]):
    print(f"  {atk}: {n:,}  ({n/TARGET_N*100:.2f}%)")

# ── Step 3: 청크별 벡터화 샘플링 ─────────────────────────────────────────────
sample_probs = {atk: sample_targets[atk] / active[atk] for atk in active}

print("\nStep 3: 배치 샘플링 중...")
collected = {atk: [] for atk in active}

for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE)):
    if dropped:
        chunk = chunk[~chunk["Attack"].isin(dropped)]
    for atk, prob in sample_probs.items():
        sub = chunk[chunk["Attack"] == atk]
        if len(sub) == 0:
            continue
        n_sample = min(max(1, round(len(sub) * prob)), len(sub))
        collected[atk].append(sub.sample(n=n_sample, random_state=int(rng.integers(1e6))))
    if (i + 1) % 10 == 0:
        pct = (i + 1) * CHUNK_SIZE / total_rows * 100
        print(f"  {(i+1)*CHUNK_SIZE:,}행 처리 ({pct:.1f}%)")

# ── Step 4: 목표 수 트리밍 후 저장 ───────────────────────────────────────────
print("\nStep 4: 트리밍 및 저장 중...")
frames = []
for atk, parts in collected.items():
    if not parts:
        continue
    df_atk = pd.concat(parts)
    target = sample_targets[atk]
    if len(df_atk) > target:
        df_atk = df_atk.sample(n=target, random_state=SEED)
    frames.append(df_atk)

sampled = pd.concat(frames).sample(frac=1, random_state=SEED).reset_index(drop=True)
sampled.to_csv(OUT_PATH, index=False)
print(f"  저장 완료: {OUT_PATH}  (총 {len(sampled):,}행)")

# ── Step 5: 분포 출력 ────────────────────────────────────────────────────────
print("\n=== 샘플링 후 Label 분포 ===")
label_counts = sampled["Label"].value_counts().sort_index()
for label, cnt in label_counts.items():
    name = "Benign" if label == 0 else "Attack"
    print(f"  {label} ({name}): {cnt:,}  ({cnt/len(sampled)*100:.2f}%)")

print("\n=== 샘플링 후 Attack 유형 분포 ===")
attack_counts = sampled["Attack"].value_counts()
for atk, cnt in attack_counts.items():
    print(f"  {atk}: {cnt:,}  ({cnt/len(sampled)*100:.2f}%)")

# ── Step 6: 시각화 ────────────────────────────────────────────────────────────
plot_distribution(
    label_counts=label_counts,
    attack_counts=attack_counts,
    title=f"Undersampled Distribution  N={len(sampled):,} / strategy={MINORITY_STRATEGY!r}",
    save_path=FIG_PATH,
)
