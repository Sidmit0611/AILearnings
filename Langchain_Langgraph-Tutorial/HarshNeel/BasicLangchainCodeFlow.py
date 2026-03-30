# pip install langgraph langchain-openai streamlit

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from typing import TypedDict, Literal
from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)

# Shared state — all agents read/write to this
# The supervisor is just an LLM call that outputs a routing decision — 
# it's not magic, it's a prompt. The quality of your supervisor prompt directly determines how well it routes.
class AgentState(TypedDict):
    user_input: str
    summary: str
    reel_script: str
    final_response: str
    next: str

def supervisor(state: AgentState) -> AgentState:
    prompt = f"""
    User said: "{state['user_input']}"
    Decide what to do. Reply with ONLY one word:
    - SUMMARISE  → if user wants to summarise an article
    - REEL       → if user wants a reel script (needs summary first)
    - ANSWER     → if it's a general question
    """
    result = llm.invoke([HumanMessage(content=prompt)])
    decision = result.content.strip().upper()
    return {**state, "next": decision}

def summariser_agent(state: AgentState) -> AgentState:
    result = llm.invoke([
        SystemMessage(content="You are an expert summariser. Extract the 3-5 key points clearly and concisely."),
        HumanMessage(content=f"Summarise this:\n\n{state['user_input']}")
    ])
    return {**state, "summary": result.content, "final_response": result.content}

def reel_script_agent(state: AgentState) -> AgentState:
    summary = state.get("summary") or state["user_input"]
    result = llm.invoke([
        SystemMessage(content="You write punchy Instagram Reel scripts. Hook in first 3 words, max 60 seconds."),
        HumanMessage(content=f"Write a reel script based on this:\n\n{summary}")
    ])
    return {**state, "reel_script": result.content, "final_response": result.content}

def general_agent(state: AgentState) -> AgentState:
    result = llm.invoke([HumanMessage(content=state["user_input"])])
    return {**state, "final_response": result.content}

def route(state: AgentState) -> Literal["summariser", "reel_script", "general", "__end__"]:
    decision = state.get("next", "ANSWER")
    if decision == "SUMMARISE": return "summariser"
    if decision == "REEL":      return "reel_script"
    return "general"

graph = StateGraph(AgentState)
graph.add_node("supervisor",  supervisor)
graph.add_node("summariser",  summariser_agent)
graph.add_node("reel_script", reel_script_agent)
graph.add_node("general",     general_agent)

graph.set_entry_point("supervisor")
graph.add_conditional_edges("supervisor", route)
graph.add_edge("summariser",  END)
graph.add_edge("reel_script", END)
graph.add_edge("general",     END)

app = graph.compile()

# ✅ THIS IS WHERE USER INPUT ENTERS THE SYSTEM
if __name__ == "__main__":
    print("Multi-Agent Chatbot (type 'exit' to quit)\n")
    while True:
        user_input = input("You: ").strip()      # <-- user types here
        if user_input.lower() == "exit":
            break

        result = app.invoke({                    # <-- passed into graph here
            "user_input": user_input,
            "summary": "",
            "reel_script": "",
            "final_response": "",
            "next": ""
        })

        print(f"\nAgent: {result['final_response']}\n")