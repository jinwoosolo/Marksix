import math
import pandas as pd
import streamlit as st
from src.data_loader import load_data
from src.scoring import score_numbers, split_pools
from src.wheel import candidate_tickets, optimize_tickets, unique_full_wheel_size, ticket_diagnostics
from src.ui import inject_css, hero, balls

st.set_page_config(page_title='Smart Wheel | Mark Six AI Lab', layout='wide')
inject_css(); hero('Smart Wheel V2.1','2 Core + 3 Secondary + Any 1 · 預算式 coverage optimizer')

@st.cache_data(ttl=900)
def data(): return load_data()

df = data()
model = st.selectbox('Ranking 模型',['ensemble_v2','ensemble','legacy_60_40','gap','frequency','recent'])
ranking = score_numbers(df, model=model)
core, secondary, lowest = split_pools(ranking)

st.markdown('**Core 12**'); st.markdown(balls(core,'ball ball-core'), unsafe_allow_html=True)
st.markdown('**Secondary 32**'); st.markdown(balls(secondary), unsafe_allow_html=True)
st.markdown('**Lowest 5**'); st.markdown(balls(lowest,'ball ball-low'), unsafe_allow_html=True)

st.divider()
mode = st.radio('第 6 字範圍',['Top 44（只容許 Core / Secondary）','全部 49（容許 Lowest 5）'], horizontal=True)
last_pool = list(range(1,50)) if mode.startswith('全部') else core + secondary
budget = st.number_input('每期預算 (HK$)', min_value=10, max_value=100000, value=200, step=10)
ticket_count = int(budget // 10)
overlap = st.slider('分散程度（越高越避免 tickets 重疊）', 0.10, 1.20, 0.55, 0.05)

m1,m2,m3,m4 = st.columns(4)
m1.metric('2-Core pairs', f'{math.comb(12,2):,}')
m2.metric('3-Secondary triples', f'{math.comb(32,3):,}')
m3.metric('5字 Skeletons', f'{math.comb(12,2)*math.comb(32,3):,}')
m4.metric('Unique full-wheel tickets', f'{unique_full_wheel_size(core,secondary,last_pool):,}')

st.info('V2.1 唔再為每個 5 字 skeleton 隨機塞一個第六字，而係直接建立可代表嘅 6 字結構：**2C+4S、3C+3S**，以及選擇全部49時嘅 **2C+3S+1L**。')

if st.button('產生智能組合', type='primary'):
    with st.spinner('建立候選組合並做 score / overlap / number-balance optimization...'):
        score_map = dict(zip(ranking['number'].astype(int), ranking['score'].astype(float)))
        cand = candidate_tickets(core, secondary, last_pool=last_pool, score_map=score_map, max_candidates=60000)
        tickets = optimize_tickets(cand, score_map, ticket_count=ticket_count, overlap_penalty=overlap)
    st.success(f'已產生 {len(tickets)} 注；總成本 HK${len(tickets)*10:,}；候選池 {len(cand):,} 注')
    out = pd.DataFrame({f'N{i+1}':[t[i] for t in tickets] for i in range(6)})
    out.insert(0,'Ticket',range(1,len(out)+1))
    st.dataframe(out, use_container_width=True, hide_index=True)
    st.markdown('#### 結構診斷')
    st.dataframe(pd.DataFrame(ticket_diagnostics(tickets,core,secondary,lowest)), use_container_width=True, hide_index=True)
    st.download_button('下載 CSV', out.to_csv(index=False).encode('utf-8-sig'), 'smart_wheel_v21_tickets.csv', 'text/csv')

st.caption('增加注數會增加覆蓋，但唔會令單一六合彩組合本身變得更容易開出。Optimizer 只係喺固定預算內分配覆蓋。')
