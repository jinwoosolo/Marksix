from __future__ import annotations
import pandas as pd
from .scoring import score_numbers, split_pools
from .metrics import (
    random_core_expectation, bootstrap_ci, monte_carlo_core_mean_pvalue,
    pool_composition_probability, strategy_coverage_probability,
)

NUM_COLS = [f'n{i}' for i in range(1, 7)]


def walk_forward_core_backtest(df: pd.DataFrame, model: str = 'ensemble_v2', core_size: int = 12,
                               test_draws: int = 500, min_history: int = 100) -> pd.DataFrame:
    if len(df) <= min_history:
        raise ValueError('Not enough history')
    start = max(min_history, len(df) - test_draws)
    rows = []
    for i in range(start, len(df)):
        hist = df.iloc[:i]
        ranking = score_numbers(hist, model=model, top_n=core_size)
        core, secondary, lowest = split_pools(ranking, core_size=core_size)
        core_set, sec_set, low_set = set(core), set(secondary), set(lowest)
        actual = set(int(x) for x in df.iloc[i][NUM_COLS].tolist())
        extra = int(df.iloc[i]['extra'])
        c_hits = len(core_set & actual)
        s_hits = len(sec_set & actual)
        l_hits = len(low_set & actual)
        rows.append({
            'date': df.iloc[i]['date'],
            'main_hits': c_hits,
            'core_hits': c_hits,
            'secondary_hits': s_hits,
            'lowest_hits': l_hits,
            'strategy_coverable': int(c_hits >= 2 and s_hits >= 3),
            'exact_2_3_1': int(c_hits == 2 and s_hits == 3 and l_hits == 1),
            'extra_hit_core': int(extra in core_set),
            'extra_hit_secondary': int(extra in sec_set),
            'extra_hit_lowest': int(extra in low_set),
            'core': tuple(sorted(core_set)),
            'secondary': tuple(sorted(sec_set)),
            'lowest': tuple(sorted(low_set)),
            'actual': tuple(sorted(actual)),
            'extra': extra,
        })
    return pd.DataFrame(rows)


def summarize_core_backtest(bt: pd.DataFrame, core_size: int = 12):
    hits = bt['main_hits'].to_numpy(dtype=float)
    expected = random_core_expectation(core_size)
    lo, hi = bootstrap_ci(hits)
    cover_baseline = strategy_coverage_probability()
    cover_rate = float(bt['strategy_coverable'].mean()) if 'strategy_coverable' in bt else float('nan')
    exact_rate = float(bt['exact_2_3_1'].mean()) if 'exact_2_3_1' in bt else float('nan')
    exact_baseline = pool_composition_probability(2, 3, 1)
    return {
        'draws': len(bt),
        'avg_main_hits': float(hits.mean()),
        'random_expected': expected,
        'edge_abs': float(hits.mean() - expected),
        'edge_pct': float((hits.mean() / expected - 1) * 100),
        'ci_low': float(lo),
        'ci_high': float(hi),
        'p_value': monte_carlo_core_mean_pvalue(hits, core_size=core_size),
        'hit_2_plus': float((hits >= 2).mean()),
        'hit_3_plus': float((hits >= 3).mean()),
        'hit_4_plus': float((hits >= 4).mean()),
        'strategy_cover_rate': cover_rate,
        'strategy_random_baseline': cover_baseline,
        'strategy_edge_pct': float((cover_rate / cover_baseline - 1) * 100) if cover_baseline else float('nan'),
        'exact_2_3_1_rate': exact_rate,
        'exact_2_3_1_random': exact_baseline,
    }


def composition_table(bt: pd.DataFrame) -> pd.DataFrame:
    g = (bt.groupby(['core_hits', 'secondary_hits', 'lowest_hits'])
           .size().reset_index(name='draws'))
    g['observed_rate'] = g['draws'] / len(bt)
    g['random_rate'] = g.apply(lambda r: pool_composition_probability(
        int(r.core_hits), int(r.secondary_hits), int(r.lowest_hits)), axis=1)
    g['relative_vs_random_pct'] = (g['observed_rate'] / g['random_rate'] - 1) * 100
    return g.sort_values(['draws', 'core_hits', 'secondary_hits'], ascending=[False, False, False]).reset_index(drop=True)


def rolling_strategy_rates(bt: pd.DataFrame, window: int = 100) -> pd.DataFrame:
    x = bt[['date', 'strategy_coverable', 'main_hits']].copy()
    x['coverage_rate'] = x['strategy_coverable'].rolling(window, min_periods=max(20, window // 2)).mean()
    x['core_avg_hits'] = x['main_hits'].rolling(window, min_periods=max(20, window // 2)).mean()
    return x
