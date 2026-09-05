from __future__ import annotations
import numpy as np
import pandas as pd
from .features import number_features, zscore, percentile_rank

MODEL_NAMES = ['ensemble_v2', 'ensemble', 'legacy_60_40', 'gap', 'frequency', 'recent', 'random']


def _legacy(f: pd.DataFrame) -> pd.Series:
    return 0.60 * zscore(f['freq_all']) + 0.40 * zscore(f['gap'])


def _recent(f: pd.DataFrame) -> pd.Series:
    return 0.55 * zscore(f['freq_30']) + 0.30 * zscore(f['freq_60']) + 0.15 * zscore(f['freq_120'])


def _ensemble_v1(f: pd.DataFrame) -> pd.Series:
    return (
        0.25 * zscore(f['freq_all']) +
        0.30 * zscore(f['freq_medium']) +
        0.25 * zscore(f['freq_short']) +
        0.10 * zscore(f['trend_short_vs_all']) -
        0.05 * zscore(f['gap_log']) -
        0.05 * zscore(f['in_prev_draw'])
    )


def _ensemble_v2(f: pd.DataFrame) -> pd.Series:
    """Robust rank blend across long/medium/recent frequency and gap signals.

    It is deliberately transparent and should only be promoted if walk-forward
    validation beats the baseline. Scores are rankings, not probabilities.
    """
    components = pd.DataFrame({
        'long': percentile_rank(f['freq_all']),
        'm250': percentile_rank(f['freq_250']),
        'm120': percentile_rank(f['freq_120']),
        'm60': percentile_rank(f['freq_60']),
        'm30': percentile_rank(f['freq_30']),
        'gap': percentile_rank(f['gap_log']),
        'prev_penalty': percentile_rank(f['in_prev_draw']),
    })
    # Gap is kept because V2's first 1,000-draw experiment showed it was among
    # the stronger simple signals, but its weight remains modest.
    return (
        0.18 * components['long'] +
        0.18 * components['m250'] +
        0.17 * components['m120'] +
        0.17 * components['m60'] +
        0.15 * components['m30'] +
        0.15 * components['gap'] -
        0.03 * components['prev_penalty']
    )


def score_numbers(history: pd.DataFrame, model: str = 'ensemble_v2', top_n: int = 12) -> pd.DataFrame:
    f = number_features(history)
    model = model.lower()
    if model == 'legacy_60_40':
        f['score'] = _legacy(f)
    elif model == 'frequency':
        f['score'] = zscore(f['freq_all'])
    elif model == 'recent':
        f['score'] = _recent(f)
    elif model == 'gap':
        f['score'] = zscore(f['gap'])
    elif model == 'ensemble':
        f['score'] = _ensemble_v1(f)
    elif model == 'ensemble_v2':
        f['score'] = _ensemble_v2(f)
    elif model == 'random':
        rng = np.random.default_rng(20260905 + len(history))
        f['score'] = rng.random(len(f))
    else:
        raise ValueError(f'Unknown model: {model}')
    f = f.sort_values(['score', 'number'], ascending=[False, True]).reset_index(drop=True)
    f['rank'] = np.arange(1, len(f) + 1)
    f['tier'] = np.where(f['rank'] <= top_n, 'Core', np.where(f['rank'] <= 44, 'Secondary', 'Lowest'))
    return f


def split_pools(ranking: pd.DataFrame, core_size: int = 12, coverage_size: int = 44):
    nums = ranking.sort_values('rank')['number'].astype(int).tolist()
    core = nums[:core_size]
    covered = nums[:coverage_size]
    secondary = [n for n in covered if n not in core]
    lowest = nums[coverage_size:]
    return core, secondary, lowest
