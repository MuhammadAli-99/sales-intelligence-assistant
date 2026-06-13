import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import importlib
import app.llm_engine
importlib.reload(app.llm_engine)
from app.llm_engine import generate_sql, generate_insight

import streamlit as st
import plotly.express as px
from app.bigquery_client import run_query

st.set_page_config(
    page_title="German Market Intelligence",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #e8eaf6 0%, #e3f2fd 40%, #e8f5e9 100%); min-height: 100vh; }
    .main .block-container { padding: 2rem 3rem; max-width: 1400px; }
    .navbar {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.7); backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.9); border-radius: 16px;
        padding: 1rem 2rem; margin-bottom: 2rem;
    }
    .navbar-brand { font-size: 18px; font-weight: 700; color: #1a1a2e; }
    .navbar-links { display: flex; gap: 2rem; font-size: 14px; color: #555; font-weight: 500; }
    .hero { text-align: center; padding: 2rem 0 1.5rem; }
    .hero h1 { font-size: 2.8rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.5rem; letter-spacing: -0.5px; }
    .hero p { font-size: 1.05rem; color: #666; max-width: 600px; margin: 0 auto; }
    .cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; margin: 2rem 0; }
    .feature-card {
        background: rgba(255,255,255,0.65); backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.9); border-radius: 20px;
        padding: 1.5rem; transition: all 0.2s ease;
    }
    .feature-card:hover { background: rgba(255,255,255,0.85); transform: translateY(-2px); }
    .card-icons { display: flex; gap: 8px; margin-bottom: 1rem; }
    .card-icon {
        width: 40px; height: 40px; border-radius: 10px;
        background: rgba(255,255,255,0.9); display: flex;
        align-items: center; justify-content: center;
        font-size: 18px; border: 1px solid rgba(0,0,0,0.06);
    }
    .card-title { font-size: 1.15rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.4rem; }
    .card-desc { font-size: 0.82rem; color: #888; line-height: 1.55; margin-bottom: 1rem; }
    .card-tag { display: inline-flex; align-items: center; gap: 4px; background: rgba(0,0,0,0.06); border-radius: 20px; padding: 4px 10px; font-size: 11px; color: #555; font-weight: 500; }
    .card-blue { background: linear-gradient(135deg, rgba(232,240,254,0.8), rgba(224,242,254,0.8)); }
    .card-peach { background: linear-gradient(135deg, rgba(255,243,224,0.8), rgba(255,236,210,0.8)); }
    .card-mint { background: linear-gradient(135deg, rgba(232,245,233,0.8), rgba(224,247,250,0.8)); }
    .card-purple { background: linear-gradient(135deg, rgba(243,232,255,0.8), rgba(237,231,246,0.8)); }
    .query-section {
        background: rgba(255,255,255,0.7); backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.9); border-radius: 20px;
        padding: 2rem; margin: 1.5rem 0;
    }
    .query-label { font-size: 1rem; font-weight: 600; color: #1a1a2e; margin-bottom: 1rem; }
    .example-btn {
        display: block; width: 100%; text-align: left;
        background: rgba(255,255,255,0.8); border: 1px solid rgba(0,0,0,0.08);
        border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
        font-size: 13px; color: #333; cursor: pointer;
        transition: all 0.15s ease;
    }
    .example-btn:hover { background: rgba(255,255,255,1); border-color: #667eea; color: #667eea; }
    .results-section {
        background: rgba(255,255,255,0.7); backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.9); border-radius: 20px;
        padding: 2rem; margin: 1.5rem 0;
    }
    .insight-card {
        background: linear-gradient(135deg, rgba(232,240,254,0.9), rgba(237,231,246,0.9));
        border: 1px solid rgba(255,255,255,0.9); border-radius: 16px;
        padding: 1.25rem 1.5rem; font-size: 0.9rem; color: #2c3e50; line-height: 1.7;
    }
    .metric-card {
        background: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.9);
        border-radius: 14px; padding: 1rem 1.25rem; text-align: center;
    }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #1a1a2e; }
    .metric-label { font-size: 0.75rem; color: #999; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }
    .stTextInput > div > div > input {
        border-radius: 12px !important; border: 1.5px solid rgba(0,0,0,0.1) !important;
        padding: 0.75rem 1rem !important; font-size: 0.95rem !important;
        background: rgba(255,255,255,0.9) !important;
    }
    .stButton > button { border-radius: 12px !important; font-weight: 600 !important; padding: 0.6rem 1.5rem !important; font-size: 0.9rem !important; }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #667eea, #764ba2) !important; border: none !important; color: white !important; }
    div[data-testid="stExpander"] { background: rgba(255,255,255,0.6) !important; border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.06) !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

TRANSLATIONS = {
    "en": {
        "title": "German Market Intelligence",
        "caption": "Ask questions about the German e-commerce market in plain English",
        "ask_header": "💬 Ask a business question",
        "input_placeholder": "e.g. Which German cities had the highest revenue in Q4 2020?",
        "analyse_button": "Analyse →",
        "sql_expander": "Generated SQL",
        "results_header": "Results",
        "insight_header": "Business Insight",
        "raw_data_header": "Raw Data",
        "rows_metric": "Rows",
        "columns_metric": "Columns",
        "revenue_metric": "Total Revenue",
        "spinner_sql": "Generating SQL query...",
        "spinner_bq": "Running query on BigQuery...",
        "spinner_insight": "Generating business insight...",
        "query_failed": "Query failed",
        "lang_button": "🇩🇪 DE",
        "examples_header": "Quick questions — click to use",
        "examples": [
            "Which German cities generated the most revenue in Q4 2020?",
            "What are the top 5 product categories by revenue in Germany?",
            "How did daily purchases trend in Germany during November 2020?",
            "What is the average order value by city in Germany?",
            "Which devices do German customers use most to make purchases?"
        ],
        "cards": [
            {"title": "City Analytics", "desc": "Revenue and transactions broken down by German cities — Berlin, Munich, Hamburg and more.", "icons": ["🏙️", "📊"], "tag": "Geo insights", "style": "card-blue"},
            {"title": "Product Intelligence", "desc": "Top performing categories and products in the German e-commerce market.", "icons": ["📦", "📈"], "tag": "Product data", "style": "card-purple"},
            {"title": "Device & Behaviour", "desc": "How German customers browse and buy — desktop vs mobile vs tablet trends.", "icons": ["💻", "📱"], "tag": "UX insights", "style": "card-mint"},
            {"title": "Revenue Trends", "desc": "Daily, weekly and monthly revenue patterns including seasonal German retail events.", "icons": ["💶", "📅"], "tag": "Finance", "style": "card-peach"},
            {"title": "AI Insights", "desc": "Every query comes with a Claude-generated business insight tailored for the DACH market.", "icons": ["🤖", "🧠"], "tag": "Claude AI", "style": "card-purple"},
            {"title": "Live BigQuery", "desc": "Queries run directly on Google BigQuery public datasets — real data, real results.", "icons": ["☁️", "⚡"], "tag": "BigQuery", "style": "card-blue"},
        ]
    },
    "de": {
        "title": "Deutsche Markt-Intelligenz",
        "caption": "Stellen Sie Fragen zum deutschen E-Commerce-Markt auf Deutsch — powered by BigQuery + Claude AI",
        "ask_header": "💬 Stellen Sie eine Geschäftsfrage",
        "input_placeholder": "z.B. Welche deutschen Städte hatten den höchsten Umsatz in Q4 2020?",
        "analyse_button": "Analysieren →",
        "sql_expander": "Generiertes SQL",
        "results_header": "Ergebnisse",
        "insight_header": "Geschäftseinblick",
        "raw_data_header": "Rohdaten",
        "rows_metric": "Zeilen",
        "columns_metric": "Spalten",
        "revenue_metric": "Gesamtumsatz",
        "spinner_sql": "SQL wird generiert...",
        "spinner_bq": "BigQuery wird abgefragt...",
        "spinner_insight": "Einblick wird generiert...",
        "query_failed": "Abfrage fehlgeschlagen",
        "lang_button": "🇬🇧 EN",
        "examples_header": "Schnellfragen — klicken zum Verwenden",
        "examples": [
            "Welche deutschen Städte erzielten im Q4 2020 den höchsten Umsatz?",
            "Was sind die Top-5-Produktkategorien nach Umsatz in Deutschland?",
            "Wie entwickelten sich die täglichen Käufe in Deutschland im November 2020?",
            "Was ist der durchschnittliche Bestellwert nach Stadt in Deutschland?",
            "Welche Geräte nutzen deutsche Kunden am häufigsten für Einkäufe?"
        ],
        "cards": [
            {"title": "Stadtanalyse", "desc": "Umsatz und Transaktionen nach deutschen Städten — Berlin, München, Hamburg.", "icons": ["🏙️", "📊"], "tag": "Geo-Einblicke", "style": "card-blue"},
            {"title": "Produktintelligenz", "desc": "Top-Kategorien und Produkte im deutschen E-Commerce-Markt.", "icons": ["📦", "📈"], "tag": "Produktdaten", "style": "card-purple"},
            {"title": "Gerät & Verhalten", "desc": "Wie deutsche Kunden surfen und kaufen — Desktop vs. Mobil vs. Tablet.", "icons": ["💻", "📱"], "tag": "UX-Einblicke", "style": "card-mint"},
            {"title": "Umsatztrends", "desc": "Tägliche, wöchentliche und monatliche Umsatzmuster inkl. saisonaler Ereignisse.", "icons": ["💶", "📅"], "tag": "Finanzen", "style": "card-peach"},
            {"title": "KI-Einblicke", "desc": "Jede Abfrage enthält einen Claude-generierten Einblick für den DACH-Markt.", "icons": ["🤖", "🧠"], "tag": "Claude KI", "style": "card-purple"},
            {"title": "Live BigQuery", "desc": "Abfragen laufen direkt auf Google BigQuery öffentlichen Datensätzen.", "icons": ["☁️", "⚡"], "tag": "BigQuery", "style": "card-blue"},
        ]
    }
}

if "language" not in st.session_state:
    st.session_state.language = "en"

t = TRANSLATIONS[st.session_state.language]

st.markdown(f"""
<div class="navbar">
    <div class="navbar-brand">🇩🇪 MarketIQ</div>
    <div class="navbar-links">
        <span>Dashboard</span>
        <span>Analytics</span>
        <span>Reports</span>
        <span>About</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_hero, col_lang = st.columns([5, 1])
with col_hero:
    st.markdown(f"""
    <div class="hero">
        <h1>{t['title']}</h1>
        <p>{t['caption']}</p>
    </div>
    """, unsafe_allow_html=True)
with col_lang:
    st.write("")
    st.write("")
    next_lang = "de" if st.session_state.language == "en" else "en"
    if st.button(t["lang_button"], use_container_width=True, key="lang_switch"):
        st.session_state.language = next_lang
        st.rerun()

cards_html = '<div class="cards-grid">'
for card in t["cards"]:
    cards_html += f"""
    <div class="feature-card {card['style']}">
        <div class="card-icons">
            <div class="card-icon">{card['icons'][0]}</div>
            <div class="card-icon">{card['icons'][1]}</div>
        </div>
        <div class="card-title">{card['title']}</div>
        <div class="card-desc">{card['desc']}</div>
        <span class="card-tag">◉ {card['tag']}</span>
    </div>"""
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown(f'<div class="query-section"><div class="query-label">{t["ask_header"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="font-size:13px; color:#888; margin-bottom:10px;">{t["examples_header"]}</div>', unsafe_allow_html=True)

for example in t["examples"]:
    if st.button(example, use_container_width=True, key=f"ex_{example[:20]}"):
        st.session_state.question = example

st.write("")
question = st.text_input(
    label="question",
    placeholder=t["input_placeholder"],
    value=st.session_state.get("question", ""),
    label_visibility="collapsed"
)

analyse_col, _ = st.columns([1, 4])
with analyse_col:
    analyse = st.button(t["analyse_button"], type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

if analyse and question:
    with st.spinner(t["spinner_sql"]):
        sql = generate_sql(question)

    with st.expander(t["sql_expander"], expanded=False):
        st.code(sql, language="sql")

    with st.spinner(t["spinner_bq"]):
        try:
            df = run_query(sql)
        except Exception as e:
            st.error(f"{t['query_failed']}: {e}")
            st.stop()

    with st.spinner(t["spinner_insight"]):
        lang_instruction = "Respond in German." if st.session_state.language == "de" else "Respond in English."
        insight = generate_insight(question, df.head(20).to_string(), lang_instruction)

    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    st.markdown(f"### {t['results_header']}")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">{t["rows_metric"]}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df.columns)}</div><div class="metric-label">{t["columns_metric"]}</div></div>', unsafe_allow_html=True)
    with m3:
        if any("revenue" in c.lower() for c in df.columns):
            rev_col = [c for c in df.columns if "revenue" in c.lower()][0]
            rev_val = f"€{df[rev_col].sum():,.2f}"
        else:
            rev_val = "—"
        st.markdown(f'<div class="metric-card"><div class="metric-value">{rev_val}</div><div class="metric-label">{t["revenue_metric"]}</div></div>', unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns([3, 2])

    with col1:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        text_cols = df.select_dtypes(exclude="number").columns.tolist()

        if text_cols and numeric_cols:
            fig = px.bar(
                df.head(15),
                x=text_cols[0],
                y=numeric_cols[0],
                title=question,
                color=numeric_cols[0],
                color_continuous_scale=["#e8eaf6", "#667eea", "#764ba2"],
                labels={numeric_cols[0]: numeric_cols[0].replace("_", " ").title()}
            )
            fig.update_layout(
                plot_bgcolor="rgba(255,255,255,0.0)",
                paper_bgcolor="rgba(255,255,255,0.0)",
                showlegend=False,
                coloraxis_showscale=False,
                font=dict(family="Inter", size=12, color="#444"),
                title=dict(font=dict(size=13, color="#1a1a2e"), x=0),
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(gridcolor="rgba(0,0,0,0.05)", tickangle=-20),
                yaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
                bargap=0.3
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

    with col2:
        st.markdown(f"**{t['insight_header']}**")
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f"**{t['raw_data_header']}**")
        st.dataframe(df, use_container_width=True, height=250)

    st.markdown('</div>', unsafe_allow_html=True)