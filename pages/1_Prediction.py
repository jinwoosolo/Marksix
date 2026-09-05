import streamlit as st
import plotly.express as px
from src.data_loader import load_data
from src.scoring import score_numbers, split_pools
from src.models import ml_ranking
from src.ui import inject_css, hero, balls

st.set_page_config(page_title='預測排名 | Mark Six AI Lab', layout='wide')
inject_css(); hero('預測排名 Prediction Engine','1–49 號碼透明排名；Score 只作排序，不等於實際中獎概率')

@st.cache_data(ttl=900)
def data(): return load_data()

df = data()
model = st.selectbox('模型',['ensemble_v2','ensemble','legacy_60_40','gap','frequency','recent','ml_logistic'])
with st.spinner('計算排名...'):
    ranking = ml_ranking(df) if model == 'ml_logistic' else score_numbers(df, model=model)
core, secondary, lowest = split_pools(ranking)

c1,c2,c3 = st.columns([1.2,3,1])
with c1:
    st.subheader('Core 12'); st.markdown(balls(core,'ball ball-core'), unsafe_allow_html=True)
with c2:
    st.subheader('Secondary 32'); st.markdown(balls(secondary), unsafe_allow_html=True)
with c3:
    st.subheader('Lowest 5'); st.markdown(balls(lowest,'ball ball-low'), unsafe_allow_html=True)

fig = px.bar(ranking.sort_values('number'), x='number', y='score', hover_data=['rank','tier'])
fig.update_layout(height=390, margin=dict(l=10,r=10,t=25,b=10), xaxis_dtick=1)
st.plotly_chart(fig, use_container_width=True)

cols = [c for c in ['rank','number','score','tier','freq_all','freq_30','freq_60','freq_120','freq_250','gap'] if c in ranking.columns]
st.dataframe(ranking[cols], use_container_width=True, hide_index=True)
st.caption('ensemble_v2 係一個透明 rank blend；是否優於舊模型必須由 Backtest / Model Lab 結果決定。')
