from __future__ import annotations
import numpy as np
import pandas as pd
from .features import number_features, zscore


def score_numbers(history: pd.DataFrame, model: str = 'ensemble', top_n: int = 12) -> pd.DataFrame:
    f = number_features(history)
    model = model.lower()
    if model == 'legacy_60_40':
        # Reproduces V1 spirit: frequency + gap, but normalized for comparability.
        f['score'] = 0.60*zscore(f['freq_all']) + 0.40*zscore(f['gap'])
    elif model == 'frequency':
        f['score'] = zscore(f['freq_all'])
    elif model == 'recent':
        f['score'] = 0.65*zscore(f['freq_short']) + 0.35*zscore(f['freq_medium'])
    elif model == 'gap':
        f['score'] = zscore(f['gap'])
    elif model == 'ensemble':
        # Conservative statistical blend; weights are intentionally transparent.
        f['score'] = (
            0.25*zscore(f['freq_all']) +
            0.30*zscore(f['freq_medium']) +
            0.25*zscore(f['freq_short']) +
            0.10*zscore(f['trend_short_vs_all']) -
            0.05*zscore(f['gap_log']) -
            0.05*zscore(f['in_prev_draw'])
        )
    elif model == 'random':
        rng = np.random.default_rng(20260905 + len(history))
        f['score'] = rng.random(len(f))
    else:
        raise ValueError(f'Unknown model: {model}')
    f = f.sort_values(['score','number'], ascending=[False,True]).reset_index(drop=True)
    f['rank'] = np.arange(1, len(f)+1)
    f['tier'] = np.where(f['rank'] <= top_n, 'Core', np.where(f['rank'] <= 44, 'Secondary', 'Lowest'))
    return f


def split_pools(ranking: pd.DataFrame, core_size: int = 12, coverage_size: int = 44):
    nums = ranking.sort_values('rank')['number'].astype(int).tolist()
    core = nums[:core_size]
    covered = nums[:coverage_size]
    secondary = [n for n in covered if n not in core]
    lowest = nums[coverage_size:]
    return core, secondary, lowest
