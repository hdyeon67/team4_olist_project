import numpy as np
import pandas as pd
from .config import CFG

def build_early_exposure(os: pd.DataFrame, cfg: CFG) -> pd.DataFrame:
    """
    목적:
    - 셀러별 '초기(첫 K개 주문)' 구간을 정의하고, 초기 노출(exposure)을 생성합니다.
    - 사용자님 셀(early_max_late, early_p95_late, early_severe7_rate)을 그대로 반영합니다.

    반환:
    - seller_id 단위 테이블
      early_orders, early_k_date, early_max_late, early_p95_late, early_severe7_rate
    """
    K = cfg.K_EARLY_ORDERS

    # seller별 주문 순번(시간순) 부여
    os = os.sort_values(["seller_id", "order_purchase_timestamp", "order_id"]).copy()
    os["order_rank"] = os.groupby("seller_id").cumcount() + 1

    # 초기 K개 주문만 추출
    early = os[os["order_rank"] <= K].copy()

    # seller별 초기 구간 요약
    seller_early = (early.groupby("seller_id", as_index=False)
        .agg(
            early_orders=("order_id","nunique"),
            early_k_date=("order_purchase_timestamp","max"),
            early_max_late=("late_days","max"),
            early_p95_late=("late_days", lambda s: float(np.percentile(s, 95))),
            early_severe7_rate=("late_days", lambda s: float(np.mean(s >= 7))),
        )
    )

    # 정확히 K개 주문이 있는 셀러만 유지 (노출량 통일)
    seller_early = seller_early[seller_early["early_orders"] == K].copy()

    return seller_early
