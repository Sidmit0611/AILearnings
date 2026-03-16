import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os, json
from datetime import datetime

load_dotenv()
st.set_page_config(page_title="Rupee Radar", page_icon="💸", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg:       #0c0e14;
    --card:     #12151e;
    --card2:    #161923;
    --border:   #1e2535;
    --accent:   #f5a623;
    --blue:     #5b9cf6;
    --green:    #3ecf8e;
    --text:     #ffffff;
    --text2:    #b8c4d4;
    --text3:    #6b7a99;
    --sans:     'Manrope', sans-serif;
    --display:  'Space Grotesk', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--bg) !important; }
.block-container { padding: 2rem 2.5rem 3rem 2.5rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── BRAND ── */
.brand {
    font-family: var(--display);
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.brand-sub {
    font-size: 0.82rem;
    color: var(--text3);
    font-weight: 400;
    margin-top: 4px;
    letter-spacing: 0.02em;
}

/* ── FILTER LABELS ── */
.flabel {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    margin-bottom: 6px;
}

/* ── DIVIDER ── */
.divider { height: 1px; background: var(--border); margin: 20px 0; }

/* ── KPI CARDS ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.kpi {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 26px;
    position: relative;
    overflow: hidden;
}
.kpi::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-l::after { background: var(--accent); }
.kpi-m::after { background: var(--blue); }
.kpi-r::after { background: var(--green); }

.kpi-label {
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    margin-bottom: 12px;
}
.kpi-val {
    font-family: var(--display);
    font-size: 2.6rem;
    font-weight: 700;
    line-height: 1;
    color: var(--text);
}
.kpi-val.amber { color: var(--accent); }
.kpi-val.gn    { color: var(--green); font-size: 1.9rem; }
.kpi-sub {
    font-size: 0.78rem;
    color: var(--text3);
    margin-top: 10px;
    font-weight: 500;
}
.kpi-badge {
    display: inline-block;
    background: rgba(245,166,35,0.1);
    border: 1px solid rgba(245,166,35,0.25);
    color: var(--accent);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border-radius: 6px;
    text-transform: uppercase;
}

/* ── SECTION TITLE ── */
.sec {
    font-family: var(--display);
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text2);
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

/* ── SELECTBOX ── */
div[data-baseweb="select"] > div {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    min-height: 44px !important;
}
div[data-baseweb="select"] * { color: var(--text) !important; }
div[data-baseweb="popover"] { background: var(--card2) !important; border: 1px solid var(--border) !important; }

/* ── BUTTON ── */
.stButton > button {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text2) !important;
    border-radius: 10px !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    transition: all 0.15s !important;
    font-family: var(--sans) !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(245,166,35,0.06) !important;
}

/* ── TRANSACTION LOG TABLE ── */
.txh {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text3);
    padding: 8px 6px 12px 6px;
    border-bottom: 2px solid var(--border);
}
.txd {
    font-size: 0.88rem;
    color: var(--text2);
    padding: 10px 6px;
    font-weight: 500;
    line-height: 1.4;
}
.txamt {
    font-family: var(--display);
    font-size: 0.96rem;
    font-weight: 700;
    color: var(--accent);
    padding: 10px 6px;
}
.txpay {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text);
    padding: 10px 6px;
    line-height: 1.3;
}
.txdesc {
    font-size: 0.82rem;
    color: var(--text3);
    padding: 10px 6px;
    line-height: 1.5;
}
.txrow-div { height: 1px; background: var(--border); opacity: 0.6; }

/* ── NO DATA ── */
.no-data {
    text-align: center;
    padding: 80px 20px;
    color: var(--text3);
    font-size: 1rem;
    font-weight: 500;
}

/* ═══════════════ MOBILE ═══════════════ */
@media (max-width: 768px) {
    .block-container { padding: 1.25rem 1rem 2rem 1rem !important; }

    /* KPI stack */
    .kpi-row { grid-template-columns: 1fr !important; gap: 12px !important; margin-bottom: 24px !important; }
    .kpi { padding: 20px 22px !important; }
    .kpi-val { font-size: 2.2rem !important; }
    .kpi-val.gn { font-size: 1.6rem !important; }
    .kpi-label { font-size: 0.72rem !important; }
    .kpi-sub { font-size: 0.76rem !important; }

    /* Stack all columns */
    [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }

    /* Larger selects for touch */
    div[data-baseweb="select"] > div { min-height: 48px !important; font-size: 1rem !important; }

    /* Bigger buttons */
    .stButton > button { width: 100% !important; min-height: 48px !important; font-size: 0.92rem !important; }

    /* Transaction log */
    .txh  { font-size: 0.68rem !important; }
    .txd  { font-size: 0.84rem !important; padding: 8px 4px !important; }
    .txamt{ font-size: 0.9rem !important;  padding: 8px 4px !important; }
    .txpay{ font-size: 0.86rem !important; padding: 8px 4px !important; }
    .txdesc { display: none !important; }

    .brand { font-size: 1.5rem !important; }
    .sec { font-size: 0.76rem !important; }
    .flabel { font-size: 0.72rem !important; }
}

@media (max-width: 480px) {
    .block-container { padding: 1rem 0.75rem 1.5rem 0.75rem !important; }
    .kpi-val { font-size: 2rem !important; }
    .kpi-val.gn { font-size: 1.4rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ───────────────────────────────────────────────────
def auto_categorize(row):
    KW = {
        "🍽️ Dining & Cafes":        ["restaurant","cafe","dhaba","lassi","skanda","star bazaar","bazaar"],
        "🛵 Online Food Delivery":   ["swiggy","zomato","blinkit","instamart"],
        "🛒 Groceries":              ["grocery","kirana","bigbasket","grofers","zepto"],
        "🥦 Vegetables & Fruits":    ["vegetable","sabzi","fruit","market","mandi","million"],
        "🥛 Milk & Dairy":           ["milk","dairy","amul","nandini"],
        "🚗 Transport & Fuel":       ["uber","ola","rapido","metro","petrol","fuel","irctc","flight"],
        "💪 Health & Fitness":       ["pharmacy","hospital","clinic","doctor","medicine","apollo","gym"],
        "📺 OTT & Subscriptions":    ["netflix","spotify","prime","hotstar","youtube","disney"],
        "🌐 Internet & Phone Bills": ["jio","airtel","bsnl","broadband","recharge","internet"],
        "🏡 Household Supplies":     ["amazon","flipkart","household","cleaning"],
        "✈️ Travel & Hotels":        ["hotel","booking","makemytrip","goibibo","oyo"],
        "💳 CC Bill":                ["standard chartered","hdfc","icici credit","axis credit","cc bill"],
        "💸 Transfers & Payments":   ["transfer","neft","imps","upi","sent","pay"],
    }
    text = f"{row.get('credited_to','')} {row.get('description','')} {row.get('additional_description','')}".lower()
    for cat, kws in KW.items():
        if any(k in text for k in kws):
            return cat
    return "💸 Transfers & Payments"

def parse_date(val):
    if not val or str(val).strip() == "": return pd.NaT
    val = str(val).strip()
    for fmt in ["%d-%B-%Y","%d-%b-%Y","%d-%b-%y","%d-%m-%Y","%Y-%m-%d","%d/%m/%Y","%d %B %Y","%d %b %Y"]:
        try: return datetime.strptime(val, fmt)
        except: continue
    try: return pd.to_datetime(val, dayfirst=True)
    except: return pd.NaT

def chart_base(fig, height=280):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope", color="#b8c4d4", size=12),
        margin=dict(l=8, r=8, t=8, b=8), height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0, font=dict(size=12, color="#b8c4d4")),
    )
    fig.update_xaxes(gridcolor="#1a2030", linecolor="#1e2535", tickfont=dict(size=12, color="#6b7a99"))
    fig.update_yaxes(gridcolor="#1a2030", linecolor="#1e2535", tickfont=dict(size=12, color="#6b7a99"))
    return fig

COLORS = ["#f5a623","#5b9cf6","#3ecf8e","#f87171","#a78bfa","#22d3ee","#fb923c","#ec4899","#84cc16","#e879f9"]

# ─── Load Data ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_raw = os.getenv("GOOGLE_CREDS_JSON")
        if not creds_raw: return pd.DataFrame()
        creds = Credentials.from_service_account_info(json.loads(creds_raw), scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(os.getenv("SHEET_ID","1WeJECZJijBNH3WVABLoKqrNroSzIzW5qGo18T3QW-W4")).sheet1
        data = sheet.get_all_records()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(data)
        df.columns = [c.lower().strip() for c in df.columns]
        df.rename(columns={"recipient":"credited_to","description from text message":"description","additional description":"additional_description"}, inplace=True)
        df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(r"[^\d.]","",regex=True), errors="coerce").fillna(0)
        df["date"] = pd.to_datetime(df["date"].apply(parse_date)).dt.normalize()
        df.dropna(subset=["date"], inplace=True)
        df["month_num"]  = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%B")
        df["year"]       = df["date"].dt.year
        if "category" not in df.columns or df["category"].astype(str).str.strip().eq("").all():
            df["category"] = df.apply(auto_categorize, axis=1)
        else:
            df["category"] = df["category"].astype(str).str.strip().replace("Other (specify below)","")
            mask = df["category"].eq("")
            df.loc[mask,"category"] = df[mask].apply(auto_categorize, axis=1)
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ─── Load ──────────────────────────────────────────────────────
df_all = load_data()
if df_all.empty:
    st.markdown('<div class="no-data">⬡ No transaction data found</div>', unsafe_allow_html=True)
    st.stop()

# ─── HEADER ────────────────────────────────────────────────────
col_left, col_center, col_right = st.columns([1, 4, 1])
with col_center:
    st.markdown('<div style="text-align:center"><div class="brand">💸 RUPEE RADAR</div><div class="brand-sub">Personal Expense Tracker</div></div>', unsafe_allow_html=True)
with col_right:
    st.markdown('<div style="padding-top:8px"></div>', unsafe_allow_html=True)
    if st.button("⟳ Sync"):
        st.cache_data.clear()
        st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─── FILTERS ───────────────────────────────────────────────────
years = sorted(df_all["year"].unique(), reverse=True)
col_y, col_m, col_c = st.columns(3)

with col_y:
    st.markdown('<div class="flabel">Year</div>', unsafe_allow_html=True)
    selected_year = st.selectbox("yr", years, label_visibility="collapsed")

df_year = df_all[df_all["year"] == selected_year]
available_months = df_year[["month_num","month_name"]].drop_duplicates().sort_values("month_num")
month_options = ["All Months"] + available_months["month_name"].tolist()

with col_m:
    st.markdown('<div class="flabel">Month</div>', unsafe_allow_html=True)
    selected_month = st.selectbox("mo", month_options, label_visibility="collapsed")

df_mf = df_year.copy() if selected_month == "All Months" else df_year[df_year["month_name"] == selected_month]
cat_options = ["All Categories"] + sorted(df_mf["category"].dropna().unique().tolist())

with col_c:
    st.markdown('<div class="flabel">Category</div>', unsafe_allow_html=True)
    selected_cat = st.selectbox("ca", cat_options, label_visibility="collapsed")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─── APPLY FILTER ──────────────────────────────────────────────
df = df_mf.copy()
if selected_cat != "All Categories":
    df = df[df["category"] == selected_cat]

period = selected_month if selected_month != "All Months" else f"All of {selected_year}"
if selected_cat != "All Categories":
    period = f"{selected_cat} · {period}"

# ─── KPI ───────────────────────────────────────────────────────
total   = df["amount"].sum()
n_txns  = len(df)
top_cat = df.groupby("category")["amount"].sum().idxmax() if n_txns > 0 else "—"
top_cat_clean = top_cat.split(" ",1)[-1] if n_txns > 0 and " " in top_cat else top_cat

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi kpi-l">
    <div class="kpi-label">Total Spent</div>
    <div class="kpi-val amber">₹{total:,.0f}</div>
    <div class="kpi-sub"><span class="kpi-badge">{period}</span></div>
  </div>
  <div class="kpi kpi-m">
    <div class="kpi-label">Transactions</div>
    <div class="kpi-val">{n_txns}</div>
    <div class="kpi-sub">recorded entries</div>
  </div>
  <div class="kpi kpi-r">
    <div class="kpi-label">Top Category</div>
    <div class="kpi-val gn">{top_cat_clean}</div>
    <div class="kpi-sub">highest spend</div>
  </div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.markdown('<div class="no-data">No transactions for this period.</div>', unsafe_allow_html=True)
    st.stop()

# ─── CHARTS ROW 1 ──────────────────────────────────────────────
c1, c2 = st.columns([3, 2], gap="large")

with c1:
    st.markdown('<div class="sec">Daily Spending</div>', unsafe_allow_html=True)
    daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
    daily.columns = ["date","amount"]
    fig1 = go.Figure(go.Bar(
        x=daily["date"], y=daily["amount"],
        marker=dict(color=daily["amount"], colorscale=[[0,"#1a2535"],[0.5,"#b45309"],[1,"#f5a623"]], line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig1.update_layout(bargap=0.3, xaxis_title="", yaxis_title="")
    st.plotly_chart(chart_base(fig1, 280), use_container_width=True, config={"displayModeBar":False})

with c2:
    st.markdown('<div class="sec">Category Breakdown</div>', unsafe_allow_html=True)
    cat_data = df.groupby("category")["amount"].sum().reset_index().sort_values("amount")
    cat_data["label"] = cat_data["category"].str.split(" ",n=1).str[-1]
    fig2 = go.Figure(go.Bar(
        x=cat_data["amount"], y=cat_data["label"], orientation="h",
        marker=dict(color=COLORS[:len(cat_data)], line=dict(width=0)),
        text=[f"₹{v:,.0f}" for v in cat_data["amount"]],
        textposition="outside",
        textfont=dict(size=12, color="#b8c4d4"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig2.update_layout(
        xaxis_title="", yaxis_title="",
        yaxis=dict(tickfont=dict(size=12, color="#b8c4d4")),
        margin=dict(l=4, r=80, t=8, b=8),
    )
    st.plotly_chart(chart_base(fig2, 280), use_container_width=True, config={"displayModeBar":False})

# ─── CHART ROW 2 ───────────────────────────────────────────────
st.markdown('<div class="sec" style="margin-top:12px">Monthly Trend</div>', unsafe_allow_html=True)
monthly = df_year.groupby(["month_num","month_name"])["amount"].sum().reset_index().sort_values("month_num")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=monthly["month_name"], y=monthly["amount"],
    mode="lines+markers" if len(monthly) > 1 else "markers",
    line=dict(color="#f5a623", width=2.5, shape="spline"),
    marker=dict(size=8, color="#f5a623", line=dict(color="#0c0e14", width=2)),
    fill="tozeroy", fillcolor="rgba(245,166,35,0.07)",
    hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
))
fig3.update_layout(xaxis_title="", yaxis_title="")
st.plotly_chart(chart_base(fig3, 220), use_container_width=True, config={"displayModeBar":False})

# ─── TRANSACTION LOG ───────────────────────────────────────────
CATEGORIES = [
    "🏠 House Rent","🧹 House Maintenance & Maid","🛒 Groceries",
    "🥦 Vegetables & Fruits","🥛 Milk & Dairy","🏡 Household Supplies",
    "🍽️ Dining & Cafes","🛵 Online Food Delivery","🚗 Transport & Fuel",
    "🅿️ Parking","🔥 Cooking Gas","💪 Health & Fitness",
    "📺 OTT & Subscriptions","🌐 Internet & Phone Bills","✈️ Travel & Hotels",
    "🎀 Decoration & Gifts","👕 Laundry & Clothing","💸 Transfers & Payments",
    "💳 CC Bill",
]

def update_category_in_sheet(sheet_row_0based, new_category):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(json.loads(os.getenv("GOOGLE_CREDS_JSON")), scopes=scopes)
        sheet = gspread.authorize(creds).open_by_key(
            os.getenv("SHEET_ID","1WeJECZJijBNH3WVABLoKqrNroSzIzW5qGo18T3QW-W4")
        ).sheet1
        sheet.update_cell(sheet_row_0based + 2, 5, new_category)
        return True
    except Exception as e:
        st.error(f"Update failed: {e}")
        return False

st.markdown('<div class="sec" style="margin-top:12px">Transaction Log</div>', unsafe_allow_html=True)

cols = ["date","amount","credited_to","category","description","additional_description"]
cols = [c for c in cols if c in df.columns]
tbl = df[cols].copy()
tbl["_sheet_row"] = tbl.index
tbl["date"]   = tbl["date"].dt.strftime("%d %b %Y")
tbl["amount"] = tbl["amount"].apply(lambda x: f"₹{x:,.0f}")
tbl = tbl.sort_values("date", ascending=False).reset_index(drop=True)

# Table header
hc = st.columns([1.2, 1.0, 1.8, 2.2, 3.5, 1.5])
for col, lbl in zip(hc, ["Date","Amount","Paid To","Category","Description","Info"]):
    col.markdown(f"<div class='txh'>{lbl}</div>", unsafe_allow_html=True)

if "cat_changes" not in st.session_state:
    st.session_state.cat_changes = {}

for idx, row in tbl.iterrows():
    sr  = int(row["_sheet_row"])
    cur = st.session_state.cat_changes.get(sr, row["category"])
    if cur not in CATEGORIES: cur = CATEGORIES[0]

    rc = st.columns([1.2, 1.0, 1.8, 2.2, 3.5, 1.5])
    rc[0].markdown(f"<div class='txd'>{row['date']}</div>", unsafe_allow_html=True)
    rc[1].markdown(f"<div class='txamt'>{row['amount']}</div>", unsafe_allow_html=True)
    rc[2].markdown(f"<div class='txpay'>{row.get('credited_to','')}</div>", unsafe_allow_html=True)
    sel = rc[3].selectbox("c", CATEGORIES, index=CATEGORIES.index(cur), key=f"cat_{sr}", label_visibility="collapsed")
    rc[4].markdown(f"<div class='txdesc'>{row.get('description','')}</div>", unsafe_allow_html=True)
    rc[5].markdown(f"<div class='txdesc'>{row.get('additional_description','')}</div>", unsafe_allow_html=True)
    st.markdown("<div class='txrow-div'></div>", unsafe_allow_html=True)

    if sel != row["category"]:
        st.session_state.cat_changes[sr] = sel
    elif sr in st.session_state.cat_changes and st.session_state.cat_changes[sr] == row["category"]:
        del st.session_state.cat_changes[sr]

# Save bar
pending = st.session_state.cat_changes
if pending:
    n = len(pending)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    cm, cs, cd = st.columns([5, 1, 1])
    cm.markdown(f"<div style='font-size:0.86rem;font-weight:600;color:#f5a623;padding-top:12px'>⬡ {n} unsaved change(s)</div>", unsafe_allow_html=True)
    with cs:
        if st.button("✓ Save", key="save_btn"):
            saved = sum(1 for sr, cat in pending.items() if update_category_in_sheet(sr, cat))
            if saved == n:
                st.success(f"✅ {saved} update(s) saved!")
                st.session_state.cat_changes = {}
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Some updates failed.")
    with cd:
        if st.button("✕ Discard", key="discard_btn"):
            st.session_state.cat_changes = {}
            st.rerun()