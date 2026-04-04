from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END, START

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
    state['total'] = state["total_usd"] * exchange_rate_USD  # Converting the total value of my portfolio from USD to INR using the exchange rate.
    return state

def chooseConversion(state: PortfolioState) -> str:
    if state["target_currency"] not in ['INR', 'EUR']:
        return "Unsupported Currency"
    else:
        return state["target_currency"]

def UnsupportedCurrency(state: PortfolioState) -> PortfolioState:
    print(f"Currency {state['target_currency']} is not supported for conversion.")
    state['total'] = -1.0 # Setting total to -1 to indicate an error in conversion due to unsupported currency.
    return state

## Creating Node
builder = StateGraph(PortfolioState)
builder.add_node("calc_total_usd", calc_total_usd)
builder.add_node("convert_to_inr", convert_to_inr)
builder.add_node("convert_total_eur", convert_total_eur)
builder.add_node("UnsupportedCurrency", UnsupportedCurrency)

## Creating Edges
builder.add_edge(START, "calc_total_usd")
builder.add_conditional_edges(
    "calc_total_usd",
    chooseConversion,
    {
        "INR": "convert_to_inr",
        "EUR": "convert_total_eur",
        "Unsupported Currency": "UnsupportedCurrency"
    }    
)
builder.add_edge("convert_to_inr", END)
builder.add_edge("convert_total_eur", END)
builder.add_edge("UnsupportedCurrency", END)

graph = builder.compile()

print(graph.invoke({"amount_usd": 1000.0, "target_currency": "INR"}))