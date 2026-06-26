# estilos.py
import streamlit as st

def cargar_css_industrial():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        
        :root {
            color-scheme: light !important;
        }
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }

        h1 {
            font-family: 'Inter', sans-serif;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            color: #334155 !important;
            letter-spacing: -0.05em;
            margin-bottom: 5px !important;
        }
        h2, h3 {
            font-weight: 700 !important;
            color: #334155 !important;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff !important;
            padding: 16px !important;
            border-radius: 12px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        }
        div[data-testid="stMetric"] label {
            color: #64748b !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            font-family: 'JetBrains Mono', monospace;
        }

        div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03) !important;
        }

        @media (max-width: 768px) {
            h1 { font-size: 1.4rem !important; }
            h2 { font-size: 1.2rem !important; }
            h3, h4, h5 { font-size: 1.05rem !important; }
            
            div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
                padding: 12px !important;
                border-radius: 10px !important;
            }

            div[data-testid="stWidgetLabel"] p {
                font-size: 11px !important;
                white-space: normal !important;
                word-break: keep-all !important;
                line-height: 1.2 !important;
            }
            
            div[data-testid="stMetric"] { padding: 10px 8px !important; }
            div[data-testid="stMetric"] label, 
            div[data-testid="stMetric"] [data-testid="stMetricLabel"] p { 
                font-size: 10px !important;
                white-space: normal !important;
                overflow: visible !important;
                text-overflow: unset !important;
                line-height: 1.1 !important;
                display: block !important;
            }
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 1.2rem !important; }

            div[data-testid="stForm"] div[data-testid="stHorizontalBlock"],
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {
                display: grid !important;
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 10px !important;
            }

            div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] {
                display: grid !important;
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 10px !important;
            }
            
            div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"]:nth-last-of-type(-n+2) {
                grid-template-columns: 1fr !important;
            }

            div[data-testid="stHorizontalBlock"] > div {
                width: 100% !important;
                min-width: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMarkdownContainer"]) {
                display: flex !important;
                flex-direction: column !important;
                gap: 4px !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)