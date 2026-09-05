from __future__ import annotations
from collections import Counter
import numpy as np
import pandas as pd

NUM_COLS = [f'n{i}' for i in range(1,7)]


def number_features(history: pd.DataFrame, short_window: int = 30, medium_window: int = 100) -> pd.DataFrame:
    if history.empty:
        raise ValueError('History is empty')
    draws = history[NUM_COLS].to_numpy(dtype=int)
    total = len(draws)
    flat_all = draws.ravel()
    flat_s = draws[-min(short_window,total):].ravel()
    flat_m = draws[-min(medium_window,total):].ravel()
    c_all, c_s, c_m = Counter(flat_all), Counter(flat_s), Counter(flat_m)
    rows = []
    for n in range(1,50):
        gap = total
        for i, d in enumerate(draws[::-1]):
            if n in d:
                gap = i
                break
        prev = 1 if n in draws[-1] else 0
        f_all = c_all[n] / max(total*6,1)
        f_s = c_s[n] / max(len(flat_s),1)
        f_m = c_m[n] / max(len(flat_m),1)
        rows.append({
            'number':n,
            'freq_all':f_all,
            'freq_short':f_s,
            'freq_medium':f_m,
            'trend_short_vs_all':f_s-f_all,
            'trend_medium_vs_all':f_m-f_all,
            'gap':gap,
            'gap_log':np.log1p(gap),
            'in_prev_draw':prev,
        })
    return pd.DataFrame(rows)


def zscore(series: pd.Series) -> pd.Series:
    s = series.astype(float)
    sd = s.std(ddof=0)
    return (s-s.mean()) / (sd if sd > 1e-12 else 1.0)
