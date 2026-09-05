import math
from src.metrics import (
    random_core_expectation, random_hit_distribution,
    pool_composition_probability, strategy_coverage_probability,
)


def test_random_expectation():
    assert abs(random_core_expectation() - 72/49) < 1e-12


def test_hit_distribution_sums_one():
    d = random_hit_distribution()
    assert abs(sum(d.values()) - 1.0) < 1e-10


def test_pool_composition_distribution_sums_one():
    total = 0.0
    for c in range(7):
        for s in range(7-c):
            total += pool_composition_probability(c, s, 6-c-s)
    assert abs(total - 1.0) < 1e-10


def test_strategy_coverage_between_zero_one():
    p = strategy_coverage_probability()
    assert 0 < p < 1
