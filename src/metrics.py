from __future__ import annotations
import math
import numpy as np
from scipy.stats import hypergeom


def random_core_expectation(core_size: int = 12, draw_size: int = 6, population: int = 49) -> float:
    return core_size * draw_size / population


def random_hit_distribution(core_size: int = 12, draw_size: int = 6, population: int = 49):
    return {k: float(hypergeom.pmf(k, population, core_size, draw_size)) for k in range(0, min(core_size, draw_size) + 1)}


def bootstrap_ci(values, n_boot: int = 3000, seed: int = 42, alpha: float = 0.05):
    a = np.asarray(values, dtype=float)
    if len(a) == 0:
        return (float('nan'), float('nan'))
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(a, size=len(a), replace=True).mean() for _ in range(n_boot)])
    return tuple(np.quantile(means, [alpha / 2, 1 - alpha / 2]).tolist())


def monte_carlo_core_mean_pvalue(observed, core_size: int = 12, draw_size: int = 6,
                                  population: int = 49, n_sim: int = 20000, seed: int = 42):
    """One-sided Monte Carlo p-value under the exact random hypergeometric baseline."""
    a = np.asarray(observed, dtype=float)
    if len(a) == 0:
        return float('nan')
    rng = np.random.default_rng(seed)
    obs = a.mean()
    sims = rng.hypergeometric(core_size, population - core_size, draw_size, size=(n_sim, len(a))).mean(axis=1)
    return float((np.sum(sims >= obs) + 1) / (n_sim + 1))


def pool_composition_probability(core_hits: int, secondary_hits: int, lowest_hits: int,
                                 core_n: int = 12, secondary_n: int = 32, lowest_n: int = 5,
                                 draw_size: int = 6) -> float:
    if core_hits + secondary_hits + lowest_hits != draw_size:
        return 0.0
    if min(core_hits, secondary_hits, lowest_hits) < 0:
        return 0.0
    if core_hits > core_n or secondary_hits > secondary_n or lowest_hits > lowest_n:
        return 0.0
    num = math.comb(core_n, core_hits) * math.comb(secondary_n, secondary_hits) * math.comb(lowest_n, lowest_hits)
    den = math.comb(core_n + secondary_n + lowest_n, draw_size)
    return num / den


def strategy_coverage_probability(core_min: int = 2, secondary_min: int = 3,
                                  core_n: int = 12, secondary_n: int = 32, lowest_n: int = 5,
                                  draw_size: int = 6) -> float:
    p = 0.0
    for c in range(draw_size + 1):
        for s in range(draw_size + 1 - c):
            l = draw_size - c - s
            if c >= core_min and s >= secondary_min:
                p += pool_composition_probability(c, s, l, core_n, secondary_n, lowest_n, draw_size)
    return float(p)
