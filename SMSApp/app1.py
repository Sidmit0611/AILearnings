from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os
import gspread
import json
import pandas as pd
from typing import Optional
from google.oauth2.service_account import Credentials
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- 1. CORS Setup (Essential for the new Frontend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Existing LLM & Sheets Setup ---
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds_json = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "1WeJECZJijBNH3WVABLoKqrNroSzIzW5qGo18T3QW-W4"
sheet = client.open_by_key(sheet_id).sheet1

class TransactionDetails(BaseModel):
    date: str = Field(description="Date of the transaction in DD-MonthName-YYYY format")
    amount: float = Field(description="Transaction amount as a numeric value")
    recipient: str = Field(description="Name of the person or merchant who received the money")
    description_from_text_message: str = Field(description="Raw description extracted from the bank SMS message")
    category: str = Field(description="Category of the transaction. One of: Food & Dining, Transport, Shopping, Utilities, Entertainment, Health, Education, Transfers, Others")
    additional_description: str = Field(description="A short, human-readable additional summary of the transaction")

structured_llm = llm.with_structured_output(TransactionDetails)

# --- 3. Helper Logic (Moved from dashboard.py) ---
def get_processed_df():
    """Fetches raw data and cleans it for the API routes."""
    data = sheet.get_all_records()
    if not data: 
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    print(df.columns)
    print(df.shape)
    # Standardize column names to lowercase
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Clean amount and date
    df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(r"[^\d.]","",regex=True), errors="coerce").fillna(0)
    df["date_dt"] = pd.to_datetime(df["date"], errors='coerce')
    df = df.dropna(subset=["date_dt"])
    print(df.shape)
    
    # Add helper columns for filtering
    df["year"] = df["date_dt"].dt.year.astype(str)
    df["month"] = df["date_dt"].dt.strftime("%B")
    return df

# --- 4. Existing SMS Webhook ---
@app.post("/sms")
async def receive_sms(request: Request):
    data = await request.json()
    message_text = data.get("Transaction Message") or data.get("formatted_message", "")
    try:
        transaction: TransactionDetails = structured_llm.invoke(
            f"Extract the transaction details from this bank SMS message: {message_text}"
        )
        row = [
            transaction.date,
            transaction.amount,
            transaction.recipient,
            transaction.description_from_text_message,
            transaction.category,
            transaction.additional_description
        ]
        sheet.append_row(row)
        return {"status": "ok ✅", "transaction": transaction.model_dump()}
    except Exception as e:
        return {"status": "⚠️ skipped", "reason": str(e)}

# --- 5. New API Routes for Dashboard ---
@app.get("/api/filters")
async def get_filters():
    """Provides dynamic filters based on sheet data."""
    df = get_processed_df()
    if df.empty: 
        return {"years": [], "months": [], "categories": []}
    
    return {
        "years": sorted(df["year"].unique().tolist(), reverse=True),
        "months": df["month"].unique().tolist(),
        "categories": sorted(df["category"].unique().tolist())
    }

@app.get("/api/dashboard")
async def get_dashboard_data(year: Optional[str] = None, month: Optional[str] = None, category: Optional[str] = None):
    """Calculates KPIs based on selected filters."""
    df = get_processed_df()
    if df.empty: 
        return {"total_spend": "₹0", "total_transactions": 0, "top_category": "N/A"}

    # Apply Filters
    if year and year != "All": 
        df = df[df["year"] == year]
    if month and month != "All": 
        df = df[df["month"] == month]
    if category and category != "All": 
        df = df[df["category"] == category]

    total_spend = float(df["amount"].sum())
    top_cat = "N/A"
    if not df.empty:
        # Calculate top category by spend
        top_cat = df.groupby("category")["amount"].sum().idxmax()

    return {
        "total_spend": f"₹{total_spend:,.0f}",
        "total_transactions": len(df),
        "top_category": top_cat
    }