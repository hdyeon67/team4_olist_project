# src/viz.py
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_korean_loss_scan(scan: pd.DataFrame, save_path: str | None = None, dpi: int = 150):
    """
    image.png 스타일 재현:
    - 빨간 선/마커
    - 한글 제목/축 라벨
    - 모든 점에 값 라벨 표시
    - x: 1..15 고정
    """
    plt.figure(figsize=(9, 5))
    plt.plot(scan["t"], scan["loss_days"], marker="o", color="red")

    plt.xticks(scan["t"])
    plt.xlabel("n (임계일수) - 최대 허용 지연일수")
    plt.ylabel("활동 잔여 기간 손실 중앙값(vs 비지연)")
    plt.title("지연 임계값에 따른 활동 잔여 기간 손실(초기 20개 주문 기준)")
    plt.grid(True, linestyle="--", alpha=0.35)

    # ✅ 모든 점에 라벨(정수 반올림)
    for t, y in zip(scan["t"], scan["loss_days"]):
        if pd.notna(y):
            plt.text(t, y + 1, f"{int(round(y))}", ha="center", va="bottom", fontsize=9)

    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(p, bbox_inches="tight", dpi=dpi)

    plt.show()
