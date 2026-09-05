from __future__ import annotations
import streamlit as st


def inject_css():
    st.markdown('''
    <style>
    .stApp {background: linear-gradient(180deg,#0b1020 0%,#101827 55%,#0b1020 100%);}
    [data-testid="stSidebar"] {background:#0b1220;border-right:1px solid rgba(255,255,255,.08)}
    .hero {padding:22px 24px;border:1px solid rgba(255,255,255,.10);border-radius:20px;
           background:linear-gradient(135deg,rgba(46,211,183,.11),rgba(112,92,255,.10));margin-bottom:18px}
    .hero h1 {margin:0;font-size:2.05rem;letter-spacing:-.03em}
    .hero p {margin:.45rem 0 0;color:#aab4c5}
    .card {padding:16px 18px;border-radius:16px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.08)}
    .eyebrow {font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:#7f8ba3;font-weight:700}
    .big {font-size:1.7rem;font-weight:800;margin-top:.2rem}
    .ball {display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:50%;
           margin:3px;font-weight:800;background:#172338;border:1px solid rgba(255,255,255,.13)}
    .ball-core {box-shadow:0 0 0 1px rgba(46,211,183,.6) inset;background:#13342f}
    .ball-low {opacity:.45;text-decoration:line-through}
    .subtle {color:#8b97aa;font-size:.9rem}
    .status-good {color:#61d3ad;font-weight:800}.status-warn {color:#f6c85f;font-weight:800}.status-bad {color:#ff7b7b;font-weight:800}
    div[data-testid="stMetric"] {background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);padding:10px 12px;border-radius:14px}
    </style>''', unsafe_allow_html=True)


def balls(numbers, cls='ball'):
    return ''.join(f"<span class='{cls}'>{int(n):02d}</span>" for n in numbers)


def hero(title, subtitle):
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)
