import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import os


def plot_distribution(
    label_counts: pd.Series,
    attack_counts: pd.Series,
    title: str,
    save_path: str | None = None,
) -> None:
    """label_counts: index=label(int), attack_counts: index=attack name(str)"""
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(title, fontsize=13, fontweight="bold")

    # 파이 차트
    ax1 = axes[0]
    labels_name = ["Benign" if k == 0 else "Attack" for k in label_counts.index]
    _, _, autotexts = ax1.pie(
        label_counts.values,
        labels=labels_name,
        autopct="%1.2f%%",
        colors=["#4CAF50", "#F44336"],
        startangle=90,
        textprops={"fontsize": 12},
    )
    for at in autotexts:
        at.set_fontsize(11)
    ax1.set_title("Label Distribution (Benign vs Attack)", fontsize=12)

    # 수평 막대 그래프 (Benign 제외, 상위 20개)
    ax2 = axes[1]
    top = attack_counts[attack_counts.index != "Benign"].head(20)
    bars = ax2.barh(top.index[::-1], top.values[::-1], color="#2196F3")
    ax2.set_xlabel("Count", fontsize=11)
    ax2.set_title("Attack Type Distribution (Top 20, excl. Benign)", fontsize=12)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    for bar, cnt in zip(bars, top.values[::-1]):
        ax2.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{cnt:,}",
            va="center",
            fontsize=8,
        )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"그래프 저장: {save_path}")
    plt.show()
