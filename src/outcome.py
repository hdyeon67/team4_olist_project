import pandas as pd
from dateutil.relativedelta import relativedelta
from .config import CFG

def build_remaining_activity(os: pd.DataFrame, seller_early: pd.DataFrame, cfg: CFG) -> pd.DataFrame:
    """
    목적:
    - 각 셀러에 대해 '초기 K개 주문 이후' 남은 활동량(remaining activity)을 계산합니다.
    - 여기서는 가장 직관적인 'remaining_orders'를 핵심 outcome으로 둡니다.
      (초기 K 이후 발생한 delivered 주문 수)

    반환:
    - seller_id 단위 outcome 테이블: remaining_orders, remaining_active_days
    """
    K = cfg.K_EARLY_ORDERS

    # seller별로 초기 K 마지막 주문 날짜(early_k_date)를 기준점으로 사용
    anchor = seller_early[["seller_id", "early_k_date"]].copy()

    # os에서 seller_id별 order_purchase_timestamp 기준으로 초기 이후 주문만 추출
    tmp = os.merge(anchor, on="seller_id", how="inner")

    # "초기 K 이후" 주문들만
    after = tmp[tmp["order_purchase_timestamp"] > tmp["early_k_date"]].copy()

    # remaining_orders: 초기 이후 주문 수
    remaining = (after.groupby("seller_id")["order_id"]
        .nunique()
        .reset_index(name="remaining_orders")
    )

    # remaining_active_days: 초기 이후 활동 기간(마지막 - 첫)
    if len(after) > 0:
        span = (after.groupby("seller_id")["order_purchase_timestamp"]
            .agg(["min", "max"])
            .reset_index()
        )
        span["remaining_active_days"] = (span["max"] - span["min"]).dt.days.astype(int)
        span = span[["seller_id", "remaining_active_days"]]
    else:
        span = anchor[["seller_id"]].copy()
        span["remaining_active_days"] = 0

    out = anchor[["seller_id"]].merge(remaining, on="seller_id", how="left").merge(span, on="seller_id", how="left")
    out["remaining_orders"] = out["remaining_orders"].fillna(0).astype(int)
    out["remaining_active_days"] = out["remaining_active_days"].fillna(0).astype(int)

    # 참고: 초기 K건 자체는 outcome에 포함하지 않습니다(‘잔여 활동’이므로)
    out["K"] = K
    return out
