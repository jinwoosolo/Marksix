from __future__ import annotations
import streamlit as st


def inject_css():
    st.markdown('''
    <style>
    .stApp {background:linear-gradient(180deg,#0a1020 0%,#11192a 52%,#0a1020 100%)}
    [data-testid="stSidebar"] {background:#09111f;border-right:1px solid rgba(255,255,255,.08)}
    .hero {padding:24px 26px;border:1px solid rgba(255,255,255,.10);border-radius:22px;
           background:linear-gradient(135deg,rgba(46,211,183,.11),rgba(112,92,255,.12));margin-bottom:20px}
    .hero h1 {margin:0;font-size:2.1rem;letter-spacing:-.035em}
    .hero p {margin:.5rem 0 0;color:#aeb8ca}
    .ball {display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;
           margin:3px;font-weight:800;background:#18243a;border:1px solid rgba(255,255,255,.13)}
    .ball-core {box-shadow:0 0 0 1px rgba(46,211,183,.65) inset;background:#12372f}
    .ball-low {opacity:.5}
    .eyebrow {font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:#8490a5;font-weight:750}
    .research-note {padding:14px 16px;border-radius:14px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07)}
    div[data-testid="stMetric"] {background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.075);padding:11px 13px;border-radius:15px}
    </style>''', unsafe_allow_html=True)


def balls(numbers, cls='ball'):
    return ''.join(f"<span class='{cls}'>{int(n):02d}</span>" for n in numbers)


def hero(title, subtitle):
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def significance_message(summary):
    p = summary.get('p_value', 1.0)
    edge = summary.get('edge_abs', 0.0)
    if p < 0.05 and edge > 0:
        st.success(f"🟢 呢段測試期出現名義統計訊號（p={p:.4f}）。仍需獨立 holdout 及多重測試校正先可稱為穩定 edge。")
    elif edge > 0:
        st.warning(f"🟡 模型平均略高於隨機基準，但證據不足（p={p:.4f}），暫時不可視為穩定預測優勢。")
    else:
        st.error(f"🔴 模型於呢段測試期沒有高於隨機基準（p={p:.4f}）。")
