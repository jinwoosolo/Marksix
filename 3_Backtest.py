import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_data
from src.backtest import walk_forward_core_backtest,summarize_core_backtest
from src.metrics import random_hit_distribution
from src.ui import inject_css,hero

st.set_page_config(page_title='Backtest | Mark Six AI Lab',layout='wide')
inject_css(); hero('Walk-forward Backtest','Test the Core 12 hypothesis without Extra-number leakage')

@st.cache_data(ttl=900)
def data(): return load_data()
@st.cache_data(show_spinner=False)
def run(model,test_draws):
    df=data(); return walk_forward_core_backtest(df,model=model,test_draws=test_draws)

model=st.selectbox('模型',['ensemble','legacy_60_40','recent','frequency','gap'])
test_draws=st.slider('測試最近多少期',100,1000,500,50)
if st.button('開始回測',type='primary'):
    with st.spinner('逐期 walk-forward 回測...'):
        bt=run(model,test_draws); s=summarize_core_backtest(bt)
    a,b,c,d=st.columns(4)
    a.metric('Core 12 平均正選命中',f"{s['avg_main_hits']:.3f}")
    b.metric('Random 理論平均',f"{s['random_expected']:.3f}")
    c.metric('相對差異',f"{s['edge_pct']:+.2f}%")
    d.metric('單尾 permutation p',f"{s['p_value']:.4f}")
    st.write(f"95% bootstrap CI：**{s['ci_low']:.3f} – {s['ci_high']:.3f}**　｜　2+：**{s['hit_2_plus']:.1%}**　3+：**{s['hit_3_plus']:.1%}**　4+：**{s['hit_4_plus']:.1%}**")
    if s['p_value']<0.05 and s['edge_abs']>0:
        st.success('呢段測試期內，Core 12 表現高過固定 Random expectation，達到名義 5% 顯著水平。仍需 holdout / 多重測試校正後先可稱為穩定 edge。')
    else:
        st.warning('目前不足以證明 Core 12 有穩定 predictive edge。')
    hist=bt['main_hits'].value_counts().sort_index().rename_axis('hits').reset_index(name='draws')
    theoretical=random_hit_distribution(12)
    hist['observed_pct']=hist['draws']/len(bt)
    hist['random_pct']=hist['hits'].map(theoretical)
    long=hist.melt(id_vars='hits',value_vars=['observed_pct','random_pct'],var_name='series',value_name='rate')
    fig=px.bar(long,x='hits',y='rate',color='series',barmode='group')
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(bt.sort_index(ascending=False).head(100),use_container_width=True,hide_index=True)
    st.download_button('下載完整 backtest CSV',bt.to_csv(index=False).encode('utf-8-sig'),'core12_backtest.csv','text/csv')
