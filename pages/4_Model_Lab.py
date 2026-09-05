import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_data
from src.backtest import walk_forward_core_backtest, summarize_core_backtest
from src.ui import inject_css, hero

st.set_page_config(page_title='Model Lab | Mark Six AI Lab', layout='wide')
inject_css(); hero('Model Lab','同一 walk-forward 規則比較所有透明模型，包括 V2.1 Ensemble')

@st.cache_data(ttl=900)
def data(): return load_data()

@st.cache_data(show_spinner=False)
def compare(test_draws):
    rows=[]
    for model in ['legacy_60_40','frequency','recent','gap','ensemble','ensemble_v2']:
        bt=walk_forward_core_backtest(data(),model=model,test_draws=test_draws)
        s=summarize_core_backtest(bt); s['model']=model; rows.append(s)
    return pd.DataFrame(rows)

test_draws=st.slider('比較期數',100,1200,1000,50)
if st.button('比較模型',type='primary'):
    with st.spinner('執行一致條件 backtest...'):
        res=compare(test_draws)
    cols=['model','avg_main_hits','edge_pct','p_value','hit_2_plus','hit_3_plus','hit_4_plus','strategy_cover_rate','strategy_random_baseline','strategy_edge_pct','exact_2_3_1_rate']
    ranked=res[cols].sort_values(['strategy_cover_rate','avg_main_hits'],ascending=False)
    st.dataframe(ranked,use_container_width=True,hide_index=True)
    st.plotly_chart(px.bar(ranked,x='model',y='strategy_edge_pct',title='2C+3S+Any1 結構相對 Random 差異'),use_container_width=True)
    st.plotly_chart(px.bar(ranked,x='model',y='avg_main_hits',title='Core 12 平均正選命中'),use_container_width=True)
    st.warning('Model Lab 係研究工具。試得越多模型/權重，越容易 data snooping；最終應保留一段完全未參與開發嘅 holdout period。')

st.markdown('### ML model')
st.write('Prediction 頁仍保留 Logistic Regression 作實驗用途，但暫時唔加入主回測比較，避免 Streamlit walk-forward 計算過重。')
