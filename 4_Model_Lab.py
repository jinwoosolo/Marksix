import pandas as pd
import streamlit as st
from src.data_loader import load_data
from src.backtest import walk_forward_core_backtest,summarize_core_backtest
from src.ui import inject_css,hero

st.set_page_config(page_title='Model Lab | Mark Six AI Lab',layout='wide')
inject_css(); hero('Model Lab','Compare transparent models under the same walk-forward rules')
@st.cache_data(ttl=900)
def data(): return load_data()
@st.cache_data(show_spinner=False)
def compare(test_draws):
    df=data(); rows=[]
    for model in ['legacy_60_40','frequency','recent','gap','ensemble']:
        bt=walk_forward_core_backtest(df,model=model,test_draws=test_draws)
        s=summarize_core_backtest(bt); s['model']=model; rows.append(s)
    return pd.DataFrame(rows)

test_draws=st.slider('比較期數',100,800,400,50)
if st.button('比較模型',type='primary'):
    with st.spinner('執行一致條件 backtest...'):
        res=compare(test_draws)
    cols=['model','avg_main_hits','random_expected','edge_pct','ci_low','ci_high','p_value','hit_2_plus','hit_3_plus','hit_4_plus']
    st.dataframe(res[cols].sort_values('avg_main_hits',ascending=False),use_container_width=True,hide_index=True)
    st.caption('揀 model 時唔應只睇最高平均值：如果試好多模型/權重，必須保留 final holdout period，避免 data snooping。')

st.markdown('### ML model')
st.write('Prediction 頁已提供 Logistic Regression ranking 作研究用途。V2 暫時不把 ML 當成預設模型，直到它通過嚴格 out-of-sample validation。')
