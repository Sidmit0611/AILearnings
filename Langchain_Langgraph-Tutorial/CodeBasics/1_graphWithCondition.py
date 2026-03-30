from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END, START
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)

class PortfolioState(TypedDict):
    amount_usd: float
    total_usd: float
    target_currency: Literal["INR", "EUR"]
    total : float

ROI = 1.05
exchange_rate_USD = 90.0
exchange_rate_EUR = 1.2

def calc_total_usd(state: PortfolioState) -> PortfolioState:
    state['total_usd'] = state["amount_usd"] * ROI  # Assuming a 5% gain, lets say I am getting 5% fixed return on my investment, so I am calculating the total value of my portfolio in USD after the gain.
    return state

def convert_total_eur(state: PortfolioState) -> PortfolioState:
    state['total'] = state["amount_usd"] * exchange_rate_EUR  # Assuming a 5% gain, lets say I am getting 5% fixed return on my investment, so I am calculating the total value of my portfolio in EUR after the gain and conversion.
    return state

def convert_to_inr(state: PortfolioState) -> PortfolioState:
    state['total_inr'] = state["total_usd"] * exchange_rate_USD  # Converting the total value of my portfolio from USD to INR using the exchange rate.
    return state

builder = StateGraph(PortfolioState)
builder.add_node("calc_total_usd", calc_total_usd)
builder.add_node("convert_to_inr", convert_to_inr)
builder.add_node("convert_total_eur", convert_total_eur)

builder.add_edge(START, "calc_total_usd")
builder.add_edge("calc_total_usd", "convert_to_inr")
builder.add_edge("calc_total_usd", "convert_total_eur")
builder.add_edge("convert_total_eur", END)
builder.add_edge("convert_to_inr", END)

graph = builder.compile()

print(graph.invoke({"amount_usd": 1000.0}))