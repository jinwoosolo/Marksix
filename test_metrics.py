from src.metrics import random_core_expectation,random_hit_distribution

def test_random_expectation():
    assert abs(random_core_expectation()-72/49)<1e-12

def test_distribution_sums_to_one():
    d=random_hit_distribution()
    assert abs(sum(d.values())-1)<1e-10
