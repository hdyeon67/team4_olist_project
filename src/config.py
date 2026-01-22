from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class CFG:
    # --- Paths ---
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    DATA_DIR: Path = PROJECT_ROOT / "data"

    # --- Files (Olist) ---
    ORDERS_CSV: str = "olist_orders_dataset.csv"
    ORDER_ITEMS_CSV: str = "olist_order_items_dataset.csv"

    # --- Filters / Definitions ---
    ONLY_DELIVERED: bool = True

    # 셀러 분석 표본 조건: 배송완료 주문이 충분한 셀러만 (요구사항 반영)
    MIN_DELIVERED_ORDERS_PER_SELLER: int = 50

    # 초기 구간(첫 K건) 정의 (현재 그래프 유지 요구사항 반영)
    K_EARLY_ORDERS: int = 20

    # late_days 정의: (actual - estimated) 일수 중 지연만(0 미만은 0 처리)
    # "7일 이상" 등 severe 정의에 필요
    LATE_DAYS_CLIP_AT_ZERO: bool = False

    # 셀러 churn 정의 (필요시 조정 가능)
    CHURN_MONTHS: int = 3

    # Threshold sweep 범위(그래프 x축)
    # 현재 그래프 형태를 크게 바꾸지 않도록 "일수 d" 기준으로 sweep
    THRESHOLD_DAYS_LIST: tuple = tuple(range(0, 10))  # 0~9일

    # 안정성을 위한 최소 표본(노출군/비노출군 너무 작으면 제외)
    MIN_GROUP_SIZE: int = 30

    # src/config.py 안 CFG 클래스에 추가(또는 수정)
    THRESHOLD_T_START: int = 1
    THRESHOLD_T_END: int = 15
