import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_data
from src.backtest import walk_forward_core_backtest, summarize_core_backtest, composition_table, rolling_strategy_rates
from src.metrics import random_hit_distribution
from src.ui import inject_css, hero, significance_message

st.set_page_config(page_title='回測 | Mark Six AI Lab', layout='wide')
inject_css(); hero('歷史滾動回測 Walk-forward Backtest','每一期只用當時之前資料；正選6號與 Extra 完全分開')

@st.cache_data(ttl=900)
def data(): return load_data()

@st.cache_data(show_spinner=False)
def run(model, test_draws):
    return walk_forward_core_backtest(data(), model=model, test_draws=test_draws)

model = st.selectbox('模型',['ensemble_v2','ensemble','legacy_60_40','gap','frequency','recent'])
test_draws = st.slider('測試最近多少期',100,1500,1000,50)
if st.button('開始回測', type='primary'):
    with st.spinner('逐期 walk-forward 回測...'):
        bt = run(model, test_draws); s = summarize_core_backtest(bt)

    st.markdown('### A. Core 12 表現')
    a,b,c,d = st.columns(4)
    a.metric('Core 12 平均正選命中', f"{s['avg_main_hits']:.3f}")
    b.metric('Random 理論平均', f"{s['random_expected']:.3f}")
    c.metric('相對差異', f"{s['edge_pct']:+.2f}%")
    d.metric('Random Monte Carlo p', f"{s['p_value']:.4f}")
    st.write(f"95% bootstrap CI：**{s['ci_low']:.3f} – {s['ci_high']:.3f}**　｜　2+：**{s['hit_2_plus']:.1%}**　3+：**{s['hit_3_plus']:.1%}**　4+：**{s['hit_4_plus']:.1%}**")
    significance_message(s)

    st.markdown('### B. 你嘅 2 Core + 3 Secondary + Any 1 結構')
    e,f,g,h = st.columns(4)
    e.metric('可覆蓋期數率', f"{s['strategy_cover_rate']:.1%}")
    f.metric('Random partition 基準', f"{s['strategy_random_baseline']:.1%}")
    g.metric('結構相對差異', f"{s['strategy_edge_pct']:+.2f}%")
    h.metric('Exact 2/3/1', f"{s['exact_2_3_1_rate']:.1%}", delta=f"Random {s['exact_2_3_1_random']:.1%}")
    st.caption('「可覆蓋」= 當期實際開獎有 Core ≥2 且 Secondary ≥3；如果完整購買所有 2C+3S+Any1 組合，呢類 draw 結構先理論上可被捕捉。固定小預算只覆蓋其中極少部分 tickets。')

    st.markdown('### C. Pool Composition Matrix')
    comp = composition_table(bt)
    st.dataframe(comp, use_container_width=True, hide_index=True)

    st.markdown('### D. Rolling stability')
    roll = rolling_strategy_rates(bt, window=min(100, max(50, len(bt)//5)))
    long = roll.melt(id_vars='date', value_vars=['coverage_rate','core_avg_hits'], var_name='metric', value_name='value')
    fig_roll = px.line(long.dropna(), x='date', y='value', color='metric')
    st.plotly_chart(fig_roll, use_container_width=True)

    st.markdown('### E. Core hit distribution vs Random')
    hist = bt['main_hits'].value_counts().sort_index().rename_axis('hits').reset_index(name='draws')
    theoretical = random_hit_distribution(12)
    hist['observed_pct'] = hist['draws']/len(bt)
    hist['random_pct'] = hist['hits'].map(theoretical)
    long2 = hist.melt(id_vars='hits', value_vars=['observed_pct','random_pct'], var_name='series', value_name='rate')
    st.plotly_chart(px.bar(long2,x='hits',y='rate',color='series',barmode='group'), use_container_width=True)

    st.markdown('### F. 最近回測明細')
    display_cols=['date','core_hits','secondary_hits','lowest_hits','strategy_coverable','exact_2_3_1','extra']
    st.dataframe(bt[display_cols].sort_index(ascending=False).head(150), use_container_width=True, hide_index=True)
    st.download_button('下載完整 backtest CSV', bt.to_csv(index=False).encode('utf-8-sig'), 'marksix_v21_backtest.csv', 'text/csv')
