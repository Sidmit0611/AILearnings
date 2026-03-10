from fastapi import FastAPI, Request
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os
import gspread
from google.oauth2.service_account import Credentials
load_dotenv()

app = FastAPI()

import os
print("GROQ KEY:", os.getenv("GROQ_API_KEY"))
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

### ------------------------------- Google Sheets Setup -------------------------------
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("smart-expense-tracker-creds.json", scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "1PVJXZ86PE8Q4ZLeB5l245aLYUkQlteKPwp3Cyb4PQgc"
sheet = client.open_by_key(sheet_id).sheet1
### ----------------------------------------------------------------------------------

class TransactionDetails(BaseModel):
    date: str = Field(description="Date of the transaction in DD-MonthName-YYYY format")
    amount: float = Field(description="Transaction amount as a numeric value")
    credited_to: str = Field(description="Name of the person or merchant who received the money")
    description: str = Field(description="A short, human-readable summary of the transaction")

structured_llm = llm.with_structured_output(TransactionDetails)


def store_in_google_sheets(transaction: TransactionDetails):
    """Appends a transaction row to Google Sheets. Adds headers if the sheet is empty."""
    headers = ["date", "amount", "credited_to", "description"]

    # If sheet is empty, add headers first
    existing_data = sheet.get_all_values()
    if not existing_data:
        sheet.append_row(headers)

    # Append the transaction as a new row
    row = [
        transaction.date,
        transaction.amount,
        transaction.credited_to,
        transaction.description
    ]
    sheet.append_row(row)
    print("Transaction saved to Google Sheets ✅")


@app.post("/sms")
async def receive_sms(request: Request):
    data = await request.json()
    print("Received SMS:", data)
    message_text = data.get("Transaction Message") or data.get("formatted_message", "")
    try:
        transaction: TransactionDetails = structured_llm.invoke(
            f"Extract the transaction details from this bank SMS message: {message_text}"
        )
        print("Parsed Transaction:", transaction.model_dump())
        store_in_google_sheets(transaction)
        return {
            "status": "ok ✅",
            "transaction": transaction.model_dump()
        }
    except Exception as e:
        print("Error parsing transaction:", str(e))
        return {"status": "⚠️ skipped", "reason": "Not a valid transaction SMS"}