import streamlit as st
from src.data_loader import load_data
from src.scoring import score_numbers, split_pools
from src.ui import inject_css, hero, balls
from src.metrics import random_core_expectation, strategy_coverage_probability

st.set_page_config(page_title='Mark Six AI Lab V2.1', page_icon='◉', layout='wide')
inject_css()
hero('Mark Six AI Lab V2.1', '透明預測模型 · Walk-forward 驗證 · 2 Core + 3 Secondary + Any 1 Smart Wheel')

@st.cache_data(ttl=900)
def get_data():
    return load_data()

try:
    df = get_data()
except Exception as e:
    st.error(f'無法載入歷史數據：{e}')
    st.info('首次啟動會嘗試由舊版 public repository 自動取得 marksix.csv。')
    st.stop()

latest = df.iloc[-1]
model = st.sidebar.selectbox('首頁模型', ['ensemble_v2','ensemble','legacy_60_40','gap','frequency','recent'], index=0)
ranking = score_numbers(df, model=model)
core, secondary, lowest = split_pools(ranking)

c1,c2,c3,c4 = st.columns(4)
c1.metric('歷史期數', f'{len(df):,}')
c2.metric('最新日期', str(latest['date']))
c3.metric('Random Core 12 理論平均', f'{random_core_expectation():.3f}')
c4.metric('2+3+Any Random結構率', f'{strategy_coverage_probability():.1%}')

st.markdown('### 最新攪珠')
left, right = st.columns([4,1])
with left:
    st.markdown(balls([latest[f'n{i}'] for i in range(1,7)]), unsafe_allow_html=True)
with right:
    st.caption('特別號（獨立計算）')
    st.markdown(balls([latest['extra']]), unsafe_allow_html=True)

st.markdown('### 下一期模型 Ranking')
a,b,c = st.columns([1.3,3.2,1])
with a:
    st.markdown("<div class='eyebrow'>Core 12</div>", unsafe_allow_html=True)
    st.markdown(balls(core,'ball ball-core'), unsafe_allow_html=True)
    st.caption('模型最高排名 12 字；不是中獎概率。')
with b:
    st.markdown("<div class='eyebrow'>Secondary 32</div>", unsafe_allow_html=True)
    st.markdown(balls(secondary), unsafe_allow_html=True)
    st.caption('Top 44 扣除 Core 12。')
with c:
    st.markdown("<div class='eyebrow'>Lowest 5</div>", unsafe_allow_html=True)
    st.markdown(balls(lowest,'ball ball-low'), unsafe_allow_html=True)
    st.caption('只代表最低排名，不代表「不會出」。')

st.markdown('### V2.1 研究重點')
st.info('新版直接測試你提出嘅結構：開獎結果是否經常滿足 **Core ≥ 2 且 Secondary ≥ 3**。呢個條件先係「2 Core + 3 Secondary + Any 1」完整 wheel 可以覆蓋一個開獎組合嘅必要結構。')
st.markdown('左側可進入 **Prediction、Smart Wheel、Backtest、Model Lab**。Backtest 頁新增 Pool Composition Matrix、Random 結構基準及 rolling stability。')
