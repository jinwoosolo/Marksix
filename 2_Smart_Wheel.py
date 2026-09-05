import math
import pandas as pd
import streamlit as st
from src.data_loader import load_data
from src.scoring import score_numbers, split_pools
from src.wheel import candidate_tickets, optimize_tickets, wheel_space_size
from src.ui import inject_css, hero, balls

st.set_page_config(page_title='Smart Wheel | Mark Six AI Lab',layout='wide')
inject_css(); hero('Smart Wheel','2 Core + 3 Secondary + 1 · budget-aware coverage optimizer')

@st.cache_data(ttl=900)
def data(): return load_data()
df=data()
model=st.selectbox('Ranking 模型',['ensemble','legacy_60_40','recent','frequency'])
ranking=score_numbers(df,model=model)
core,secondary,lowest=split_pools(ranking)

st.markdown('**Core 12**'); st.markdown(balls(core,'ball ball-core'),unsafe_allow_html=True)
st.markdown('**Secondary 32**'); st.markdown(balls(secondary),unsafe_allow_html=True)
st.markdown('**Lowest 5**'); st.markdown(balls(lowest,'ball ball-low'),unsafe_allow_html=True)

st.divider()
mode=st.radio('第 6 字候選池',['Top 44（Core + Secondary）','全部 49'],horizontal=True)
last_pool=list(range(1,50)) if mode.startswith('全部') else core+secondary
budget=st.number_input('每期預算 (HK$)',min_value=10,max_value=100000,value=200,step=10)
ticket_price=10
ticket_count=int(budget//ticket_price)
base=math.comb(len(core),2)*math.comb(len(secondary),3)
full_variants=sum(max(0,len(last_pool)-5) for _ in range(base))

m1,m2,m3=st.columns(3)
m1.metric('2-Core 組合',f'{math.comb(12,2):,}')
m2.metric('3-Secondary 組合',f'{math.comb(32,3):,}')
m3.metric('5字 Skeletons',f'{base:,}')
st.warning(f'如果每個 5 字 skeleton 再把可用第 6 字全部「全餐」，原始生成量約 {full_variants:,} 次（當中會有大量重複 ticket）。所以 V2 預設用 budget optimizer，而不是無限制全餐。')

if st.button('產生智能組合',type='primary'):
    with st.spinner('建立 candidate pool 並做 diversification...'):
        cand=candidate_tickets(core,secondary,last_pool=last_pool,max_candidates=30000)
        score_map=dict(zip(ranking['number'].astype(int),ranking['score'].astype(float)))
        tickets=optimize_tickets(cand,score_map,ticket_count=ticket_count)
    st.success(f'已產生 {len(tickets)} 注；預算 HK${len(tickets)*ticket_price:,}')
    out=pd.DataFrame({f'N{i+1}':[t[i] for t in tickets] for i in range(6)})
    out.insert(0,'Ticket',range(1,len(out)+1))
    st.dataframe(out,use_container_width=True,hide_index=True)
    st.download_button('下載 CSV',out.to_csv(index=False).encode('utf-8-sig'),'smart_wheel_tickets.csv','text/csv')

st.caption('Optimizer 目標係喺指定注數下平衡模型分數與 ticket 之間的重疊程度；並不改變單一六合彩組合本身的基本隨機性。')
