from __future__ import annotations
import numpy as np
import pandas as pd
from .scoring import score_numbers
from .metrics import random_core_expectation, bootstrap_ci, permutation_mean_pvalue

NUM_COLS = [f'n{i}' for i in range(1,7)]


def walk_forward_core_backtest(df: pd.DataFrame, model: str = 'ensemble', core_size: int = 12, test_draws: int = 500, min_history: int = 100) -> pd.DataFrame:
    if len(df) <= min_history:
        raise ValueError('Not enough history')
    start = max(min_history, len(df)-test_draws)
    rows = []
    for i in range(start, len(df)):
        hist = df.iloc[:i]
        ranking = score_numbers(hist, model=model, top_n=core_size)
        core = set(ranking.head(core_size)['number'].astype(int))
        actual = set(int(x) for x in df.iloc[i][NUM_COLS].tolist())
        extra = int(df.iloc[i]['extra'])
        main_hits = len(core & actual)
        rows.append({
            'date':df.iloc[i]['date'],
            'main_hits':main_hits,
            'extra_hit':int(extra in core),
            'core':tuple(sorted(core)),
            'actual':tuple(sorted(actual)),
            'extra':extra,
        })
    return pd.DataFrame(rows)


def summarize_core_backtest(bt: pd.DataFrame, core_size: int = 12):
    hits = bt['main_hits'].to_numpy(dtype=float)
    expected = random_core_expectation(core_size)
    lo, hi = bootstrap_ci(hits)
    return {
        'draws':len(bt),
        'avg_main_hits':float(hits.mean()),
        'random_expected':expected,
        'edge_abs':float(hits.mean()-expected),
        'edge_pct':float((hits.mean()/expected-1)*100),
        'ci_low':float(lo),
        'ci_high':float(hi),
        'p_value':permutation_mean_pvalue(hits, expected),
        'hit_2_plus':float((hits>=2).mean()),
        'hit_3_plus':float((hits>=3).mean()),
        'hit_4_plus':float((hits>=4).mean()),
    }
