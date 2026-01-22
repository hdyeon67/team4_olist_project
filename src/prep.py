import pandas as pd
import numpy as np
from .config import CFG

def build_order_seller_base(orders: pd.DataFrame, items: pd.DataFrame, cfg: CFG) -> pd.DataFrame:
    """
    목적:
    - 주문(orders)과 주문아이템(order_items)을 결합해 '주문-셀러' 단위 테이블(os)을 생성합니다.
    - delivered 주문만 대상으로 late_days(지연일수)를 계산합니다.
    
    결과 컬럼(핵심):
    - seller_id, order_id, order_purchase_timestamp
    - order_estimated_delivery_date, order_delivered_customer_date
    - delivery_delay_days: (actual - estimated) 일수 (음수 가능)
    - late_days: 지연만(clip) 반영 (>=0)
    """
    # 1) orders에서 필요한 컬럼만 추림
    o = orders[[
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
        "order_delivered_customer_date",
    ]].copy()

    # 2) delivered만 남길지 여부
    if cfg.ONLY_DELIVERED:
        o = o[o["order_status"] == "delivered"].copy()

    # 3) items에서 주문-셀러 관계 생성 (한 주문에 셀러가 여러 명일 수 있으나 대개 1명)
    it = items[["order_id", "seller_id"]].copy()

    # 4) join: order_id 기준
    os = it.merge(o, on="order_id", how="inner")

    # 5) 지연 일수 계산: actual - estimated
    # delivered_customer_date가 없는 경우 제거
    os = os.dropna(subset=["order_delivered_customer_date", "order_estimated_delivery_date"]).copy()

    os["delivery_delay_days"] = (
        os["order_delivered_customer_date"] - os["order_estimated_delivery_date"]
    ).dt.days.astype(int)

    # 6) late_days: 지연만 반영 (조기배송/정시배송은 0 처리)
    if cfg.LATE_DAYS_CLIP_AT_ZERO:
        os["late_days"] = os["delivery_delay_days"].clip(lower=0).astype(int)
    else:
        os["late_days"] = os["delivery_delay_days"].astype(int)

    # 7) 시간순 정렬 (seller별 cumcount를 정확히 하기 위함)
    os = os.sort_values(["seller_id", "order_purchase_timestamp"]).reset_index(drop=True)

    return os

def filter_sellers_by_min_orders(os: pd.DataFrame, cfg: CFG) -> pd.DataFrame:
    """
    목적:
    - 배송완료 주문(=os의 row가 주문-셀러 단위이므로 order_id 기준 unique)이
      cfg.MIN_DELIVERED_ORDERS_PER_SELLER 이상인 셀러만 남깁니다.
    """
    seller_cnt = (
        os.groupby("seller_id")["order_id"]
          .nunique()
          .reset_index(name="delivered_order_cnt")
    )
    eligible = seller_cnt[seller_cnt["delivered_order_cnt"] >= cfg.MIN_DELIVERED_ORDERS_PER_SELLER]["seller_id"]

    os2 = os[os["seller_id"].isin(eligible)].copy()
    return os2
