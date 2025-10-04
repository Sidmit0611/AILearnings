from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field 
from langgraph.graph import StateGraph, END
from prompts import *
from states import *

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

"""
Now when we print the response of EPS and Price, model will return the values with some text information in it
For example, when I ran the code below, I got the following response:
**Extracted Information**

- **Price:** $150  
- **Earnings Per Share (EPS):** $5.25

But when we want the output in a structured format like JSON, we can specify that in the prompt itself.
or We can use Pydantic along with 'with_structured_output' method to get the output in structured format
in 'with_structured_output', we can specify the schema we want.

by this way, reponse will be object of Schema class and we can access the values using dot notation
e.g. response.price, response.eps
"""


# --------------------------- EXAMPLES ---------------------------
response1 = llm.invoke("Who invented Kriya Yoga?. Answer in 1 sentence")
# print(response1)

response2 = llm.with_structured_output(Schema).invoke("Extract Price and EPS from this report \n" \
                      "The price of the stock is $150 and the EPS is $5.25.")
# print(response2.price)
# print(response2.eps)

user_prompt = "Create a simple calculator web application"
prompt = planner_prompt(user_prompt) # importing prompt from prompts.py file
response3 = llm.with_structured_output(Plan).invoke(prompt) #main response for this code 
# print(response3.name)
# print(response3.description)
# print(response3.techstack)
# print(response3.features)
for file in response3.files:
    pass # remove when print statement is uncommented
    # print(f"File Path: {file.path}, Purpose: {file.purpose}")

# ----------------------------------------------------------------

# --------------------------- PLANNER NODE IN THE AGENT GRAPH ---------------------------
def planner_agent(state: dict) -> dict:
    """
    This agent will create a plan for the application to be built.
    It will take the user prompt as input and return the plan as output.
    """
    try:
        user_prompt = state["user_prompt"]
        prompt = planner_prompt(user_prompt) # importing prompt from prompts.py file
        response3 = llm.with_structured_output(Plan).invoke(prompt) #main response for this code
        return {"plan" : response3}
    except Exception as e:
        raise ValueError({"Planner did not return a valid response": str(e)})

def architect_agent(state: dict) -> dict:
    """
    This agent will take the plan created by the planner agent and break it down into explicit engineering tasks.
    It will also create a file structure for the project.
    """
    try:
        plan = state["plan"]
        prompt = architect_prompt(plan) # importing prompt from prompts.py file
        response4 = llm.with_structured_output(TaskPlan).invoke(prompt) #main response for this code
        response4.plan = plan  # Attach the original plan to the response for context
        return {"task_plan" : response4}
    except Exception as e:
        raise ValueError({"Architect did not return a valid response": str(e)})

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_edge("planner", "architect")
graph.set_entry_point("planner")


if __name__ == "__main__":
    user_prompt = "Create a simple calculator web application"
    agent = graph.compile()
    result = agent.invoke({"user_prompt": user_prompt})

    print(f"Type of Result is {type(result)}")
    for key, value in result.items():
        if key == "plan":
            print(f"{key}:")
            print(f"  Name: {value.name}")
            print(f"  Description: {value.description}")
            print(f"  Techstack: {', '.join(value.techstack)}")
            print(f"  Features: {', '.join(value.features)}")
            print(f"  Files:")
            for file in value.files:
                print(f"    - Path: {file.path}, Purpose: {file.purpose}")
        if key == "task_plan":
            print(f"{key}:")
            for step in value.implementation_steps:
                print(f"  - Filepath: {step.filepath}")
                print(f"    Task Description: {step.task_description}")
            print(f"  Original Plan Name: {value.plan.name}")
            print(f"  Original Plan Description: {value.plan.description}")
            print(f"  Original Plan Techstack: {', '.join(value.plan.techstack)}")
            print(f"  Original Plan Features: {', '.join(value.plan.features)}")
            print(f"  Original Plan Files:")
            for file in value.plan.files:
                print(f"    - Path: {file.path}, Purpose: {file.purpose}")
        else:
            print(f"{key}: {value}")
