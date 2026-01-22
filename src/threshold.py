# src/threshold.py
import pandas as pd
import numpy as np

def compute_effect_scan_median(df: pd.DataFrame, delay_col: str, y_col: str, t_start: int = 1, t_end: int = 15) -> pd.DataFrame:
    """
    사용자 제공 코드와 완전히 동일한 로직.
    - hi: delay_col >= t
    - lo: delay_col < t
    - loss_days = median(lo[y_col]) - median(hi[y_col])
    - t=1..15
    """
    rows = []
    for t in range(t_start, t_end + 1):
        hi = df[df[delay_col] >= t]
        lo = df[df[delay_col] <  t]

        # 사용자 코드 그대로: median 차이를 계산 (표본 부족 체크로 건너뛰지 않음)
        loss = lo[y_col].median() - hi[y_col].median()
        rows.append({"t": t, "loss_days": float(loss) if pd.notna(loss) else np.nan, "n_hi": int(len(hi)), "n_lo": int(len(lo))})

    return pd.DataFrame(rows)
