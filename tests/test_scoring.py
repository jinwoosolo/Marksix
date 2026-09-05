import pandas as pd
from src.scoring import score_numbers, split_pools


def sample_df(n=140):
    rows=[]
    for i in range(n):
        nums=[((i*7+j*8)%49)+1 for j in range(6)]
        nums=list(dict.fromkeys(nums))
        x=1
        while len(nums)<6:
            if x not in nums: nums.append(x)
            x+=1
        extra=1
        while extra in nums: extra+=1
        rows.append({'date':f'2020-01-{(i%28)+1:02d}',**{f'n{k+1}':nums[k] for k in range(6)},'extra':extra})
    return pd.DataFrame(rows)


def test_all_models_rank_49():
    df=sample_df()
    for model in ['legacy_60_40','frequency','recent','gap','ensemble','ensemble_v2','random']:
        r=score_numbers(df,model=model)
        assert len(r)==49
        assert sorted(r['number'].tolist())==list(range(1,50))
        core,sec,low=split_pools(r)
        assert (len(core),len(sec),len(low))==(12,32,5)
        assert len(set(core+sec+low))==49
