import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Rupee Radar", page_icon="💸", layout="wide")

# ─────────────────────────────────────────────
#  CSS — Premium Dark Financial Terminal
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg:        #080a0f;
    --surface:   #0e1117;
    --card:      #111520;
    --card2:     #141824;
    --border:    #1e2535;
    --border2:   #252d40;
    --accent:    #f59e0b;
    --accent2:   #3b82f6;
    --accent3:   #10b981;
    --danger:    #ef4444;
    --text:      #e8eaf0;
    --text2:     #8892a4;
    --text3:     #4a5568;
    --mono:      'JetBrains Mono', monospace;
    --sans:      'DM Sans', sans-serif;
    --display:   'Syne', sans-serif;
    --glow-gold: 0 0 20px rgba(245,158,11,0.15);
    --glow-blue: 0 0 20px rgba(59,130,246,0.15);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--sans) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Top command bar ── */
.command-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 0 20px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.command-bar-brand {
    font-family: var(--display);
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-right: 16px;
    white-space: nowrap;
}
.command-bar-label {
    font-family: var(--mono);
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text3);
    margin-bottom: 2px;
}

/* ── Metric cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { border-color: var(--border2); }
.kpi-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.015) 0%, transparent 60%);
    pointer-events: none;
}
.kpi-card.gold  { border-left: 3px solid var(--accent);  box-shadow: var(--glow-gold); }
.kpi-card.blue  { border-left: 3px solid var(--accent2); box-shadow: var(--glow-blue); }
.kpi-card.green { border-left: 3px solid var(--accent3); }

.kpi-label {
    font-family: var(--mono);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--text3);
    margin-bottom: 10px;
}
.kpi-value {
    font-family: var(--mono);
    font-size: 2.1rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-value.gold  { color: var(--accent); }
.kpi-value.green { color: var(--accent3); }
.kpi-sub {
    font-family: var(--sans);
    font-size: 0.72rem;
    color: var(--text3);
    margin-top: 7px;
}
.kpi-icon {
    position: absolute;
    top: 18px; right: 20px;
    font-size: 1.4rem;
    opacity: 0.2;
}

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    margin-top: 4px;
}
.section-title {
    font-family: var(--display);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text2);
}
.section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border2), transparent);
}

/* ── Chart containers ── */
.chart-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

/* ── Selectboxes ── */
div[data-baseweb="select"] > div {
    background: var(--card2) !important;
    border-color: var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
}
div[data-baseweb="select"] * { color: var(--text) !important; }

/* ── Dataframe ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }
.stDataFrame [data-testid="stDataFrameResizable"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    width: 220px !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Button ── */
.stButton > button {
    background: var(--card2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text2) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    padding: 6px 14px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Period badge ── */
.period-badge {
    display: inline-block;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: var(--accent);
    font-family: var(--mono);
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 4px;
    letter-spacing: 0.08em;
}

/* ── No data ── */
.no-data {
    text-align: center;
    padding: 80px 20px;
    color: var(--text3);
    font-family: var(--mono);
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def auto_categorize(row: pd.Series) -> str:
    KEYWORDS = {
        "🍽️ Dining & Cafes":         ["restaurant", "cafe", "dhaba", "hotel", "lassi", "corner", "skanda", "star bazaar"],
        "🛵 Online Food Delivery":    ["swiggy", "zomato", "blinkit", "instamart"],
        "🛒 Groceries":               ["grocery", "kirana", "bigbasket", "grofers", "zepto"],
        "🥦 Vegetables & Fruits":     ["vegetable", "sabzi", "fruit", "market", "mandi"],
        "🥛 Milk & Dairy":            ["milk", "dairy", "amul", "nandini"],
        "🚗 Transport & Fuel":        ["uber", "ola", "rapido", "metro", "petrol", "fuel", "irctc", "flight", "bus"],
        "💪 Health & Fitness":        ["pharmacy", "hospital", "clinic", "doctor", "medicine", "apollo", "gym", "fitness"],
        "📺 OTT & Subscriptions":     ["netflix", "spotify", "prime", "hotstar", "youtube", "disney"],
        "🌐 Internet & Phone Bills":  ["jio", "airtel", "bsnl", "broadband", "recharge", "internet"],
        "🏡 Household Supplies":      ["amazon", "flipkart", "household", "cleaning", "supplies"],
        "✈️ Travel & Hotels":         ["hotel", "booking", "makemytrip", "goibibo", "oyo", "flight"],
        "💸 Transfers & Payments":    ["transfer", "neft", "imps", "upi", "sent", "pay"],
    }
    text = f"{row.get('credited_to', '')} {row.get('description', '')} {row.get('additional_description', '')}".lower()
    for category, keywords in KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "💸 Transfers & Payments"

def parse_date(val):
    if not val or str(val).strip() == "":
        return pd.NaT
    val = str(val).strip()
    formats = [
        "%d-%B-%Y", "%d-%b-%Y", "%d-%b-%y",
        "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y",
        "%d %B %Y", "%d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(val, dayfirst=True)
    except Exception:
        return pd.NaT

def dark_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#4a5568", size=11),
        margin=dict(l=8, r=8, t=28, b=8),
        legend=dict(
            bgcolor="rgba(14,17,23,0.9)",
            bordercolor="#1e2535",
            borderwidth=1,
            font=dict(size=10, color="#8892a4"),
        ),
    )
    fig.update_xaxes(gridcolor="#141824", linecolor="#1e2535", tickfont=dict(size=10, color="#4a5568"))
    fig.update_yaxes(gridcolor="#141824", linecolor="#1e2535", tickfont=dict(size=10, color="#4a5568"))
    return fig

COLORS = ["#f59e0b", "#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316", "#ec4899"]

# ─────────────────────────────────────────────
#  Load Data
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_raw = os.getenv("GOOGLE_CREDS_JSON")
        if not creds_raw:
            return pd.DataFrame()
        creds_json = json.loads(creds_raw)
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        client = gspread.authorize(creds)
        sheet_id = os.getenv("SHEET_ID", "1WeJECZJijBNH3WVABLoKqrNroSzIzW5qGo18T3QW-W4")
        sheet = client.open_by_key(sheet_id).sheet1
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df.columns = [c.lower().strip() for c in df.columns]
        df.rename(columns={
            "recipient":                     "credited_to",
            "description from text message": "description",
            "additional description":        "additional_description",
        }, inplace=True)
        df["amount"] = df["amount"].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["date"] = df["date"].apply(parse_date)
        df.dropna(subset=["date"], inplace=True)
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        df["month_num"]  = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%B")
        df["year"]       = df["date"].dt.year
        if "category" not in df.columns or df["category"].astype(str).str.strip().eq("").all():
            df["category"] = df.apply(auto_categorize, axis=1)
        else:
            df["category"] = df["category"].astype(str).str.strip()
            mask = df["category"].eq("")
            df.loc[mask, "category"] = df[mask].apply(auto_categorize, axis=1)
        # Clean up any stuck placeholder values from previous edits
        df["category"] = df["category"].replace("Other (specify below)", "")
        mask2 = df["category"].eq("")
        df.loc[mask2, "category"] = df[mask2].apply(auto_categorize, axis=1)
        df = df.reset_index(drop=True)  # ensure clean 0-based index matching sheet rows
        return df
    except Exception as e:
        st.error(f"Connection error: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
#  Load & guard
# ─────────────────────────────────────────────
df_all = load_data()
if df_all.empty:
    st.markdown('<div class="no-data">⬡ NO TRANSACTION DATA FOUND</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  Top command bar — brand + filters + refresh
# ─────────────────────────────────────────────
years = sorted(df_all["year"].unique(), reverse=True)

col_brand, col_year, col_month, col_cat, col_spacer, col_refresh, col_time = st.columns([2, 1.2, 1.5, 1.8, 1, 1, 1.5])

with col_brand:
    st.markdown('<div style="padding-top:8px"><span style="font-family:\'Syne\',sans-serif;font-size:1.25rem;font-weight:800;color:#f59e0b;letter-spacing:0.08em">💸 RUPEE RADAR</span></div>', unsafe_allow_html=True)

with col_year:
    st.markdown('<div class="command-bar-label">YEAR</div>', unsafe_allow_html=True)
    selected_year = st.selectbox("year", years, label_visibility="collapsed")

df_year = df_all[df_all["year"] == selected_year]
available_months = df_year[["month_num","month_name"]].drop_duplicates().sort_values("month_num")
month_options = ["ALL MONTHS"] + available_months["month_name"].str.upper().tolist()

with col_month:
    st.markdown('<div class="command-bar-label">MONTH</div>', unsafe_allow_html=True)
    selected_month_display = st.selectbox("month", month_options, label_visibility="collapsed")

# Build category options from month-filtered data
if selected_month_display == "ALL MONTHS":
    df_month_filtered = df_year.copy()
else:
    df_month_filtered = df_year[df_year["month_name"] == selected_month_display.title()]

available_cats = sorted(df_month_filtered["category"].dropna().unique().tolist())
cat_options = ["ALL CATEGORIES"] + available_cats

with col_cat:
    st.markdown('<div class="command-bar-label">CATEGORY</div>', unsafe_allow_html=True)
    selected_category = st.selectbox("category", cat_options, label_visibility="collapsed")

with col_refresh:
    st.markdown('<div style="padding-top:22px"></div>', unsafe_allow_html=True)
    if st.button("↺ SYNC"):
        st.cache_data.clear()
        st.rerun()

with col_time:
    st.markdown(f'<div style="padding-top:26px;font-family:\'JetBrains Mono\',monospace;font-size:0.65rem;color:#2d3748;text-align:right">{datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:linear-gradient(90deg,#1e2535,transparent);margin-bottom:24px"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Filter
# ─────────────────────────────────────────────
# Start from month-filtered data
df = df_month_filtered.copy()
if selected_month_display == "ALL MONTHS":
    period_label = f"ALL OF {selected_year}"
else:
    period_label = f"{selected_month_display} {selected_year}"

# Apply category filter
if selected_category != "ALL CATEGORIES":
    df = df[df["category"] == selected_category]
    period_label = f"{selected_category}  ·  {period_label}"

# ─────────────────────────────────────────────
#  KPI Cards
# ─────────────────────────────────────────────
total_spend  = df["amount"].sum()
total_txns   = len(df)
top_category = df.groupby("category")["amount"].sum().idxmax() if total_txns > 0 else "—"

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card gold">
        <div class="kpi-icon">₹</div>
        <div class="kpi-label">Total Debited</div>
        <div class="kpi-value gold">₹{total_spend:,.0f}</div>
        <div class="kpi-sub"><span class="period-badge">{period_label}</span></div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">#</div>
        <div class="kpi-label">Transactions</div>
        <div class="kpi-value">{total_txns}</div>
        <div class="kpi-sub">recorded entries</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">↑</div>
        <div class="kpi-label">Top Spend Category</div>
        <div class="kpi-value green" style="font-size:1.3rem">{top_category}</div>
        <div class="kpi-sub">highest allocation</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Charts
# ─────────────────────────────────────────────
if df.empty:
    st.markdown('<div class="no-data">⬡ NO TRANSACTIONS FOR THIS PERIOD</div>', unsafe_allow_html=True)
    st.stop()

# Row 1
col_l, col_r = st.columns([3, 2], gap="medium")

with col_l:
    st.markdown('<div class="section-header"><span class="section-title">Daily Spending</span><div class="section-line"></div></div>', unsafe_allow_html=True)
    daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
    daily.columns = ["date", "amount"]
    fig = go.Figure(go.Bar(
        x=daily["date"], y=daily["amount"],
        marker=dict(
            color=daily["amount"],
            colorscale=[[0, "#1a2235"], [0.5, "#b45309"], [1, "#f59e0b"]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(bargap=0.35, xaxis_title="", yaxis_title="")
    st.plotly_chart(dark_fig(fig), use_container_width=True)

with col_r:
    st.markdown('<div class="section-header"><span class="section-title">Category Split</span><div class="section-line"></div></div>', unsafe_allow_html=True)
    cat_data = df.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=False)
    fig2 = go.Figure(go.Pie(
        labels=cat_data["category"],
        values=cat_data["amount"],
        hole=0.62,
        marker=dict(colors=COLORS, line=dict(color="#080a0f", width=2)),
        textfont=dict(family="JetBrains Mono", size=10),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig2.update_layout(
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=10)),
        margin=dict(l=0, r=0, t=10, b=10),
        annotations=[dict(
            text=f"<b>₹{total_spend:,.0f}</b>",
            x=0.5, y=0.5, font=dict(size=14, color="#f59e0b", family="JetBrains Mono"),
            showarrow=False
        )]
    )
    st.plotly_chart(dark_fig(fig2), use_container_width=True)

# Row 2
col_a, col_b = st.columns([2, 3], gap="medium")

with col_a:
    st.markdown('<div class="section-header"><span class="section-title">Category Breakdown</span><div class="section-line"></div></div>', unsafe_allow_html=True)
    fig3 = go.Figure(go.Bar(
        x=cat_data["amount"],
        y=cat_data["category"],
        orientation="h",
        marker=dict(color=COLORS[:len(cat_data)], line=dict(width=0)),
        text=[f"₹{v:,.0f}" for v in cat_data["amount"]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10, color="#8892a4"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig3.update_layout(
        xaxis_title="", yaxis_title="",
        yaxis=dict(tickfont=dict(size=11, color="#8892a4")),
        margin=dict(l=4, r=60, t=10, b=8),
    )
    st.plotly_chart(dark_fig(fig3), use_container_width=True)

with col_b:
    st.markdown('<div class="section-header"><span class="section-title">Monthly Trend</span><div class="section-line"></div></div>', unsafe_allow_html=True)
    monthly = df_year.groupby(["month_num","month_name"])["amount"].sum().reset_index().sort_values("month_num")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=monthly["month_name"], y=monthly["amount"],
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2.5, shape="spline"),
        marker=dict(size=8, color="#f59e0b", line=dict(color="#080a0f", width=2)),
        fill="tozeroy",
        fillcolor="rgba(245,158,11,0.06)",
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig4.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(dark_fig(fig4), use_container_width=True)

# ─────────────────────────────────────────────
#  Transaction Log — Row-by-row category editing
# ─────────────────────────────────────────────
CATEGORIES = [
    "🏠 House Rent",
    "🧹 House Maintenance & Maid",
    "🛒 Groceries",
    "🥦 Vegetables & Fruits",
    "🥛 Milk & Dairy",
    "🏡 Household Supplies",
    "🍽️ Dining & Cafes",
    "🛵 Online Food Delivery",
    "🚗 Transport & Fuel",
    "🅿️ Parking",
    "🔥 Cooking Gas",
    "💪 Health & Fitness",
    "📺 OTT & Subscriptions",
    "🌐 Internet & Phone Bills",
    "✈️ Travel & Hotels",
    "🎀 Decoration & Gifts",
    "👕 Laundry & Clothing",
    "💸 Transfers & Payments",
    "💳 CC Bill",
]

def update_category_in_sheet(sheet_row_0based: int, new_category: str) -> bool:
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_json = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(
            os.getenv("SHEET_ID", "1WeJECZJijBNH3WVABLoKqrNroSzIzW5qGo18T3QW-W4")
        ).sheet1
        sheet.update_cell(sheet_row_0based + 2, 5, new_category)
        return True
    except Exception as e:
        st.error(f"Sheet update failed: {e}")
        return False

st.markdown("<div class='section-header' style='margin-top:8px'><span class='section-title'>Transaction Log</span><div class='section-line'></div></div>", unsafe_allow_html=True)

# Build table — keep original df_all index as sheet row reference
cols = ["date", "amount", "credited_to", "category", "description", "additional_description"]
cols = [c for c in cols if c in df.columns]
tbl = df[cols].copy()
tbl["_sheet_row"] = tbl.index          # 0-based index = sheet row (df_all was reset_index on load)
tbl["date"] = tbl["date"].dt.strftime("%d %b %Y")
tbl["amount"] = tbl["amount"].apply(lambda x: f"₹{x:,.2f}")
tbl = tbl.sort_values("date", ascending=False).reset_index(drop=True)

# ── Table header ──
hcols = st.columns([1.2, 0.9, 1.6, 1.8, 3.2, 1.5])
for col, label in zip(hcols, ["Date", "Amount", "Paid To", "Category", "Description", "Additional Info"]):
    col.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;color:#4a5568;padding:6px 4px 4px 4px;border-bottom:1px solid #1e2535'>{label}</div>", unsafe_allow_html=True)

# ── Track pending saves ──
if "cat_changes" not in st.session_state:
    st.session_state.cat_changes = {}   # {sheet_row: new_category}

# ── Render each row ──
for idx, row in tbl.iterrows():
    sheet_row = int(row["_sheet_row"])
    current_cat = st.session_state.cat_changes.get(sheet_row, row["category"])
    # Ensure current value is in list (handles old values from sheet)
    if current_cat not in CATEGORIES:
        current_cat = CATEGORIES[0]
    cat_idx = CATEGORIES.index(current_cat)

    rcols = st.columns([1.2, 0.9, 1.6, 1.8, 3.2, 1.5])
    rcols[0].markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.78rem;color:#8892a4;padding:7px 4px'>{row['date']}</div>", unsafe_allow_html=True)
    rcols[1].markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.82rem;color:#f59e0b;padding:7px 4px'>{row['amount']}</div>", unsafe_allow_html=True)
    rcols[2].markdown(f"<div style='font-size:0.82rem;color:#e8eaf0;padding:7px 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{row.get('credited_to','')}</div>", unsafe_allow_html=True)

    selected = rcols[3].selectbox(
        label="cat",
        options=CATEGORIES,
        index=cat_idx,
        key=f"cat_{sheet_row}",
        label_visibility="collapsed",
    )

    # Track if changed
    if selected != row["category"]:
        st.session_state.cat_changes[sheet_row] = selected
    elif sheet_row in st.session_state.cat_changes and st.session_state.cat_changes[sheet_row] == row["category"]:
        del st.session_state.cat_changes[sheet_row]

    rcols[4].markdown(f"<div style='font-size:0.75rem;color:#64748b;padding:7px 4px;overflow:hidden;text-overflow:ellipsis'>{row.get('description','')}</div>", unsafe_allow_html=True)
    rcols[5].markdown(f"<div style='font-size:0.75rem;color:#64748b;padding:7px 4px'>{row.get('additional_description','')}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:#0e1117;margin:0'></div>", unsafe_allow_html=True)

# ── Save bar ──
pending_changes = st.session_state.cat_changes
if pending_changes:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    n = len(pending_changes)
    col_msg, col_save, col_discard = st.columns([4, 1, 1])
    col_msg.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#f59e0b;padding-top:10px'>⬡ {n} unsaved change(s)</div>", unsafe_allow_html=True)
    with col_save:
        if st.button("✓ SAVE", key="save_btn"):
            saved = 0
            for sr, cat in pending_changes.items():
                if update_category_in_sheet(sr, cat):
                    saved += 1
            if saved == n:
                st.success(f"✅ {saved} update(s) saved!")
                st.session_state.cat_changes = {}
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Some updates failed.")
    with col_discard:
        if st.button("✕ DISCARD", key="discard_btn"):
            st.session_state.cat_changes = {}
            st.rerun()