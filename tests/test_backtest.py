import pandas as pd
from src.backtest import walk_forward_core_backtest, summarize_core_backtest, composition_table


def sample_df(n=180):
    rows=[]
    for i in range(n):
        # deterministic but valid six distinct numbers
        nums=[]
        k=0
        while len(nums)<6:
            v=((i*11+k*7)%49)+1
            if v not in nums: nums.append(v)
            k+=1
        extra=1
        while extra in nums: extra+=1
        rows.append({'date':pd.Timestamp('2020-01-01')+pd.Timedelta(days=i),**{f'n{k+1}':nums[k] for k in range(6)},'extra':extra})
    return pd.DataFrame(rows)


def test_pool_hits_sum_six():
    bt=walk_forward_core_backtest(sample_df(),model='ensemble_v2',test_draws=40,min_history=100)
    assert ((bt.core_hits+bt.secondary_hits+bt.lowest_hits)==6).all()
    assert ((bt.strategy_coverable==((bt.core_hits>=2)&(bt.secondary_hits>=3)).astype(int))).all()


def test_summary_and_composition():
    bt=walk_forward_core_backtest(sample_df(),model='gap',test_draws=30,min_history=100)
    s=summarize_core_backtest(bt)
    assert s['draws']==30
    c=composition_table(bt)
    assert c['draws'].sum()==30
