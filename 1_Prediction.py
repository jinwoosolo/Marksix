import streamlit as st
import plotly.express as px
from src.data_loader import load_data
from src.scoring import score_numbers, split_pools
from src.models import ml_ranking
from src.ui import inject_css, hero, balls

st.set_page_config(page_title='Prediction | Mark Six AI Lab', layout='wide')
inject_css(); hero('Prediction Engine','1–49 ranking with transparent statistical and ML models')

@st.cache_data(ttl=900)
def data(): return load_data()
df=data()
model=st.selectbox('模型',['ensemble','legacy_60_40','recent','frequency','gap','ml_logistic'])
with st.spinner('計算 ranking...'):
    ranking = ml_ranking(df) if model=='ml_logistic' else score_numbers(df,model=model)
core,secondary,lowest=split_pools(ranking)

c1,c2,c3=st.columns([1.2,3,1])
with c1:
    st.subheader('Core 12'); st.markdown(balls(core,'ball ball-core'),unsafe_allow_html=True)
with c2:
    st.subheader('Secondary 32'); st.markdown(balls(secondary),unsafe_allow_html=True)
with c3:
    st.subheader('Lowest 5'); st.markdown(balls(lowest,'ball ball-low'),unsafe_allow_html=True)

fig=px.bar(ranking.sort_values('number'),x='number',y='score',hover_data=['rank','tier'])
fig.update_layout(height=390,margin=dict(l=10,r=10,t=25,b=10),xaxis_dtick=1)
st.plotly_chart(fig,use_container_width=True)

show=ranking[['rank','number','score','tier','freq_all','freq_short','freq_medium','gap']].copy()
st.dataframe(show,use_container_width=True,hide_index=True)
st.caption('Score 是模型 ranking score，不應解讀成實際中獎概率。')
