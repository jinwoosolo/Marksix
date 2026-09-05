from __future__ import annotations
import math
import numpy as np
from scipy.stats import hypergeom


def random_core_expectation(core_size: int = 12, draw_size: int = 6, population: int = 49) -> float:
    return core_size * draw_size / population


def random_hit_distribution(core_size: int = 12, draw_size: int = 6, population: int = 49):
    return {k: float(hypergeom.pmf(k, population, core_size, draw_size)) for k in range(0, min(core_size,draw_size)+1)}


def bootstrap_ci(values, n_boot: int = 3000, seed: int = 42, alpha: float = 0.05):
    a = np.asarray(values, dtype=float)
    if len(a) == 0:
        return (float('nan'), float('nan'))
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(a, size=len(a), replace=True).mean() for _ in range(n_boot)])
    return tuple(np.quantile(means, [alpha/2,1-alpha/2]).tolist())


def permutation_mean_pvalue(observed, baseline_expectation: float, n_perm: int = 10000, seed: int = 42):
    # Tests whether observed mean exceeds a fixed expectation using centered sign-flip residuals.
    a = np.asarray(observed, dtype=float)
    if len(a) == 0:
        return float('nan')
    resid = a - baseline_expectation
    obs = resid.mean()
    rng = np.random.default_rng(seed)
    perm = np.empty(n_perm)
    for i in range(n_perm):
        perm[i] = (resid * rng.choice([-1,1], size=len(resid))).mean()
    return float((np.sum(perm >= obs)+1)/(n_perm+1))
