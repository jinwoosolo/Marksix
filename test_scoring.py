import pandas as pd
from src.scoring import score_numbers,split_pools

def fake_df(n=120):
    rows=[]
    for i in range(n):
        nums=[((i*7+j*8)%49)+1 for j in range(6)]
        # Ensure uniqueness deterministically.
        nums=list(dict.fromkeys(nums))
        x=1
        while len(nums)<6:
            if x not in nums: nums.append(x)
            x+=1
        extra=next(x for x in range(1,50) if x not in nums)
        rows.append({'date':f'2020-01-{(i%28)+1:02d}',**{f'n{k+1}':nums[k] for k in range(6)},'extra':extra})
    return pd.DataFrame(rows)

def test_ranking_partition():
    r=score_numbers(fake_df(),'ensemble')
    core,secondary,low=split_pools(r)
    assert len(r)==49 and len(core)==12 and len(secondary)==32 and len(low)==5
    assert len(set(core+secondary+low))==49
