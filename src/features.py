from __future__ import annotations
from collections import Counter
import numpy as np
import pandas as pd

NUM_COLS = [f'n{i}' for i in range(1, 7)]


def _freq(draws: np.ndarray, window: int) -> Counter:
    d = draws[-min(window, len(draws)):]
    return Counter(d.ravel())


def number_features(history: pd.DataFrame, short_window: int = 30, medium_window: int = 100) -> pd.DataFrame:
    """Create per-number features using main six numbers only (Extra is excluded)."""
    if history.empty:
        raise ValueError('History is empty')
    draws = history[NUM_COLS].to_numpy(dtype=int)
    total = len(draws)
    c_all = Counter(draws.ravel())
    counters = {w: _freq(draws, w) for w in (10, 30, 60, 100, 120, 250)}
    rows = []
    for n in range(1, 50):
        gap = total
        for i, d in enumerate(draws[::-1]):
            if n in d:
                gap = i
                break
        f_all = c_all[n] / max(total * 6, 1)
        vals = {f'freq_{w}': counters[w][n] / max(min(w, total) * 6, 1) for w in counters}
        rows.append({
            'number': n,
            'freq_all': f_all,
            'freq_short': vals['freq_30'],
            'freq_medium': vals['freq_100'],
            **vals,
            'trend_10_vs_all': vals['freq_10'] - f_all,
            'trend_30_vs_all': vals['freq_30'] - f_all,
            'trend_60_vs_all': vals['freq_60'] - f_all,
            'trend_120_vs_all': vals['freq_120'] - f_all,
            'trend_250_vs_all': vals['freq_250'] - f_all,
            'trend_short_vs_all': vals['freq_30'] - f_all,
            'trend_medium_vs_all': vals['freq_100'] - f_all,
            'gap': gap,
            'gap_log': np.log1p(gap),
            'gap_sqrt': np.sqrt(gap),
            'in_prev_draw': int(n in draws[-1]),
        })
    return pd.DataFrame(rows)


def zscore(series: pd.Series) -> pd.Series:
    s = series.astype(float)
    sd = s.std(ddof=0)
    return (s - s.mean()) / (sd if sd > 1e-12 else 1.0)


def percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(method='average', pct=True)
