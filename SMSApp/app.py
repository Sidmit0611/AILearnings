from fastapi import FastAPI, Request
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import pandas as pd
load_dotenv()

# This is a simple FastAPI application that receives SMS messages
app = FastAPI()

### Loading the model
llm = ChatGroq(model="openai/gpt-oss-120b")

class TransactionDetails(BaseModel):
    date: str = Field(description="Date of the transaction in DD-MonthName-YYYY format")
    amount: float = Field(description="Transaction amount as a numeric value")
    credited_to: str = Field(description="Name of the person or merchant who received the money")
    description: str = Field(description="A short, human-readable summary of the transaction")

structured_llm = llm.with_structured_output(TransactionDetails)

@app.post("/sms")
async def receive_sms(request: Request):
    data = await request.json()
    print("Received SMS:", data)

    message_text = data.get("Transaction Message") or data.get("formatted_message", "")

    transaction: TransactionDetails = structured_llm.invoke(
        f"Extract the transaction details from this bank SMS message: {message_text}"
    )

    print("Parsed Transaction:", transaction.model_dump())

    ### Store the transaction dump in csv file to view them later, you can use pandas for this
    data = pd.DataFrame([transaction.model_dump()])
    data.to_csv("transactions.csv", index=False)
    
    return {
        "status": "ok",
        "transaction": transaction.model_dump()
    }