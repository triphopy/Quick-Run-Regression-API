from __future__ import annotations

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-top: #eef4ff;
            --bg-mid: #f8fbff;
            --bg-bottom: #f6f8fc;
            --text-strong: #122033;
            --text-body: #2c3e57;
            --text-soft: #6f7f95;
            --line-soft: #d9e1ef;
            --line-strong: #c7d3e6;
        }
        .stApp {
            background: linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 30%, var(--bg-bottom) 100%);
            color: var(--text-body);
        }
        .block-container {
            padding-top: 2.4rem;
            padding-bottom: 2.25rem;
            max-width: 1320px;
        }
        .header-wrap {
            padding-top: 0.45rem;
            padding-bottom: 0.2rem;
        }
        h1, h2, h3, .stMarkdown, .stCaption, label, p, span, div {
            color: var(--text-body);
        }
        h1, h2, h3 {
            color: var(--text-strong);
            letter-spacing: -0.02em;
        }
        [data-testid="stMarkdownContainer"] p {
            line-height: 1.45;
        }
        [data-testid="stCaptionContainer"] {
            color: var(--text-soft);
            font-size: 0.84rem;
        }
        [data-testid="stSubheader"] {
            margin-bottom: 0.35rem;
        }
        [data-testid="stSubheader"] h3 {
            font-size: 1.02rem;
            font-weight: 700;
        }
        [data-testid="stHeadingWithActionElements"] h1 {
            font-size: 1.9rem;
            margin-bottom: 0.1rem;
        }
        .stSelectbox label,
        .stTextInput label,
        .stFileUploader label {
            font-size: 0.84rem;
            font-weight: 600;
            color: var(--text-body);
        }
        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stFileUploader section {
            border-color: var(--line-soft);
            border-radius: 0.9rem;
        }
        .stFileUploader section {
            padding-top: 0.4rem;
            padding-bottom: 0.4rem;
        }
        .stButton button {
            border-radius: 0.85rem;
            min-height: 2.5rem;
            font-weight: 600;
            border: 1px solid var(--line-strong);
        }
        .stButton button[kind="tertiary"] {
            min-height: 1.8rem;
            padding: 0.1rem 0.2rem;
            border: none;
            background: transparent;
            box-shadow: none;
            color: #2f5fb8;
            justify-content: flex-end;
            font-weight: 700;
            text-decoration: underline;
            text-decoration-color: rgba(47, 95, 184, 0.28);
            text-decoration-thickness: 1px;
            text-underline-offset: 0.14rem;
        }
        .stButton button[kind="tertiary"]:hover {
            background: rgba(47, 124, 246, 0.06);
            color: #2f7cf6;
            text-decoration-color: rgba(47, 124, 246, 0.55);
        }
        .stButton button[kind="primary"] {
            box-shadow: 0 8px 18px rgba(255, 77, 89, 0.14);
        }
        .stButton button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.85);
        }
        .stMetric {
            background: rgba(255, 255, 255, 0.52);
            border: 1px solid rgba(199, 211, 230, 0.65);
            border-radius: 1rem;
            padding: 0.65rem 0.85rem;
        }
        .stMetric [data-testid="stMetricLabel"] {
            font-size: 0.78rem;
        }
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        .brand {
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: .2em;
            color: var(--text-strong);
            line-height: 1.1;
            padding-top: 0.2rem;
            margin-bottom: .05rem;
        }
        .run-status {
            text-align: center;
            background: #e7f7ef;
            color: #1ea672;
            border: 1px solid #bde7d1;
            border-radius: 999px;
            padding: .55rem .95rem;
            font-weight: 700;
            font-size: 0.86rem;
        }
        .card-shell {
            background: #ffffff;
            border: 1px solid var(--line-soft);
            border-radius: 1.25rem;
            padding: 1.25rem 1.25rem 1rem 1.25rem;
            box-shadow: 0 14px 30px rgba(27, 54, 98, 0.06);
            margin-bottom: 1.2rem;
        }
        .chip-row {
            display: flex;
            gap: .45rem;
            flex-wrap: wrap;
            margin-top: .65rem;
            margin-bottom: .25rem;
        }
        .chip {
            display: inline-block;
            padding: .3rem .68rem;
            border-radius: 999px;
            background: #eef4ff;
            color: #4f6887;
            font-size: .74rem;
            font-weight: 700;
        }
        .method-pill {
            display: inline-block;
            padding: .2rem .6rem;
            border-radius: 999px;
            font-size: .7rem;
            font-weight: 800;
        }
        .metric-card {
            color: white;
            border-radius: 1.1rem;
            padding: 0.9rem 0.95rem 1rem 0.95rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 10px 22px rgba(27, 54, 98, 0.08);
        }
        .metric-title {
            font-size: .82rem;
            opacity: .9;
        }
        .metric-value {
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.1;
            margin-top: .18rem;
        }
        .metric-sub {
            font-size: .76rem;
            margin-top: .28rem;
            opacity: .9;
        }
        .status-pass, .status-fail {
            display: inline-block;
            padding: .25rem .6rem;
            border-radius: 999px;
            font-size: .75rem;
            font-weight: 800;
            margin-bottom: .5rem;
        }
        .status-pass {
            background: #e8f8f1;
            color: #1ea672;
        }
        .status-fail {
            background: #ffecee;
            color: #e04f5f;
        }
        .stCheckbox {
            margin-top: 0.05rem;
        }
        .stCheckbox > label {
            padding-top: 0.1rem;
            padding-bottom: 0.1rem;
        }
        .stSelectbox,
        .stTextInput,
        .stFileUploader,
        .stButton,
        .stCheckbox,
        .stMarkdown,
        .stCaption {
            margin-bottom: 0.22rem;
        }
        [data-testid="column"] {
            gap: 0.35rem;
        }
        [data-testid="stHorizontalBlock"] {
            gap: 0.65rem;
        }
        .stProgress > div > div {
            border-radius: 999px;
        }
        .stProgress {
            margin-top: 0.1rem;
            margin-bottom: 0.1rem;
        }
        .stProgress > div {
            min-height: 0.45rem;
        }
        .stAlert {
            border-radius: 0.95rem;
        }
        .stExpander {
            border-color: var(--line-soft);
            border-radius: 1rem;
        }
        .table-head {
            display: grid;
            grid-template-columns: 0.08fr 0.14fr 0.42fr 0.22fr 0.14fr;
            gap: 0.65rem;
            padding: 0.2rem 0.4rem 0.4rem 0.4rem;
            margin-top: 0.35rem;
            border-bottom: 1px solid rgba(199, 211, 230, 0.8);
            color: var(--text-soft);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .meta-bar {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.7rem;
            margin: 0.35rem 0 1rem 0;
        }
        .meta-item {
            background: rgba(255, 255, 255, 0.62);
            border: 1px solid rgba(199, 211, 230, 0.75);
            border-radius: 0.95rem;
            padding: 0.75rem 0.85rem;
        }
        .meta-label {
            font-size: 0.72rem;
            color: var(--text-soft);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.18rem;
        }
        .meta-value {
            font-size: 0.94rem;
            color: var(--text-strong);
            font-weight: 700;
            line-height: 1.25;
            word-break: break-word;
        }
        .section-tight {
            margin-top: 0.35rem;
            margin-bottom: 0.45rem;
        }
        .section-help {
            margin-top: -0.15rem;
            margin-bottom: 0.35rem;
            color: var(--text-soft);
            font-size: 0.8rem;
        }
        .empty-state {
            border: 1px dashed rgba(199, 211, 230, 0.95);
            border-radius: 1rem;
            padding: 1rem 1.1rem;
            background: rgba(255, 255, 255, 0.55);
            margin: 0.4rem 0 0.8rem 0;
        }
        .empty-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-strong);
            margin-bottom: 0.18rem;
        }
        .empty-copy {
            font-size: 0.82rem;
            color: var(--text-soft);
            line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str, subtitle: str, color: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="background:{color};">
          <div class="metric-title">{title}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
