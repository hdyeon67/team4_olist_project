from pathlib import Path
import pandas as pd
from .config import CFG

def _resolve_path(data_dir: Path, filename: str) -> Path:
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return path

def load_orders_items(cfg: CFG):
    """
    목적:
    - orders, order_items CSV를 로드하고 datetime 컬럼을 파싱합니다.
    - 로컬 실행에서 재현 가능하도록 cfg.DATA_DIR 기준으로 경로를 고정합니다.
    """
    orders_path = _resolve_path(cfg.DATA_DIR, cfg.ORDERS_CSV)
    items_path = _resolve_path(cfg.DATA_DIR, cfg.ORDER_ITEMS_CSV)

    orders = pd.read_csv(
        orders_path,
        parse_dates=[
            "order_purchase_timestamp",
            "order_estimated_delivery_date",
            "order_delivered_customer_date",
        ]
    )

    items = pd.read_csv(items_path)

    return orders, items
