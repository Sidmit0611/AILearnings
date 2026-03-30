from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END, START
from dotenv import load_dotenv
load_dotenv()

### Loading the LLM
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)

### State is an object which gets passed between the objects, and all the objects can read/write to it. 
### It's a shared memory between the agents.

class PortfolioState(TypedDict):
    amount_usd: float
    total_usd: float
    total_inr: float

ROI = 1.05
exchange_rate = 90.0

### This is how define object of class in Python, we can also define it as a function as well, but for the sake of simplicity,
#  we are defining it as an object here. It is of no use, just learning purpose
my_obj : PortfolioState = {
    "amount_usd": 1000.0,
    "total_usd": 0.0,
    "total_inr": 0.0
}

### Assume that main code start from here
### Class PortfolioState is the state which is shared between the functions, and all the functions can read/write to it.
### It is there to ensure that the data is structured and we know what data is being passed between the functions, 
### and it also helps in type checking and auto-completion in IDEs.

def calc_total_usd(state: PortfolioState) -> PortfolioState:
    state['total_usd'] = state["amount_usd"] * ROI  # Assuming a 5% gain, lets say I am getting 5% fixed return on my investment, so I am calculating the total value of my portfolio in USD after the gain.
    return state

def convert_to_inr(state: PortfolioState) -> PortfolioState:
    state['total_inr'] = state["total_usd"] * exchange_rate  # Converting the total value of my portfolio from USD to INR using the exchange rate.
    return state

builder = StateGraph(PortfolioState)
builder.add_node("calc_total_usd", calc_total_usd)
builder.add_node("convert_to_inr", convert_to_inr)

builder.add_edge(START, "calc_total_usd")
builder.add_edge("calc_total_usd", "convert_to_inr")
builder.add_edge("convert_to_inr", END)

graph = builder.compile()

print(graph.invoke({"amount_usd": 1000.0}))