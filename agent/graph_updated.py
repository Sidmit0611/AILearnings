from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field 
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from prompts import *
from states import *
from dotenv import load_dotenv
from tools import *
load_dotenv()

### Loading the model
llm = ChatGroq(model="openai/gpt-oss-120b")

### Defining the agents for the graph
def planner_agent(state: dict) -> dict:
    """
    This agent will create a plan for the application to be built.
    It will take the user prompt as input and return the plan as output.
    """
    try:
        user_prompt = state["user_prompt"]
        prompt = planner_prompt(user_prompt) # importing prompt from prompts.py file
        response3 = llm.with_structured_output(Plan).invoke(prompt) #main response for this code
        
        print(response3)
        print("*********** Planner Response:*********** \n")
        print("Name of the application: ", response3.name)
        print("Description: ", response3.description)
        print("Techstack: ", response3.techstack)
        print("Features: ", response3.features)
        for file in response3.files:
            print(f"File Path: {file.file_path}, Description: {file.file_description}, Purpose: {file.file_purpose}")
    
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
        print(response4)
        return {"task_plan" : response4}
    except Exception as e:
        raise ValueError({"Architect did not return a valid response": str(e)})
    
def coder_agent(state: dict) -> dict:
    """
    This agent will take the task plan created by the architect agent and implement the tasks.
    See codebasics youtube video for more details on this implementation. Timestamp: 52:36
    If I am building something in which I have to write multiple files, I have to maintain the state of which file I am working on currently.
    So therefore, there will be internal states which I have to define
    for example, in this case, coder_state will be an internal state which will maintain the current step index and the task plan.
    Since, architect agent is returning the task plan, we can use that to initialize the coder_state when it is not present in the state dict.
    1. Check if coder_state is present in the state dict. If not, initialize it with the task plan and current_step_idx = 0
    2. Get the current step from the task plan using the current_step_idx
    3. Create the prompt for the coder agent using the current step details
    4. Invoke the LLM to get the code for the current step
    5. Write the code to the specified file path
    6. Increment the current_step_idx in the coder_state
    7. Return the updated coder_state in the state dict
    8. If all steps are completed, return status as DONE
    9. In case of any error, raise an exception
    10. Note that we are using create_react_agent to create a ReAct agent for the coder agent to use tools like read_file, write_file, get_current_directory, list_files, run_cmd
    11. This will help the coder agent to read the existing content of the file before writing new code to it.
    12. This will also help in debugging the code if any errors occur during the implementation.
    13. Finally, we will return the updated coder_state in the state dict.
    14. If all steps are completed, we will return status as DONE.
    15. In case of any error, we will raise an exception.
    16. Note that we are not using structured output here, but using create_react_agent to create a ReAct agent for the coder agent.
    17. This will help the coder agent to use tools like read_file, write_file, get_current_directory, list_files, run_cmd
    18. This will help the coder agent to read the existing content of the file before writing new code to it.
    19. This will also help in debugging the code if any errors occur during the implementation.
    20. Finally, we will return the updated coder_state in the state dict.
    21. If all steps are completed, we will return status as DONE.
    22. In case of any error, we will raise an exception.
    23. Note that we are not using structured output here, but using create_react_agent to create a ReAct agent for the coder agent.
    24. This will help the coder agent to use tools like read_file, write_file, get_current_directory, list_files, run_cmd
    25. This will help the coder agent to read the existing content of the file before writing new code to it.
    26. This will also help in debugging the code if any errors occur during the implementation.
    27. Finally, we will return the updated coder_state in the state dict.
    28. If all steps are completed, we will return status as DONE.
    """
    try:
        coder_state = state.get("coder_state") # 🚨 ‼️ here, we could have written state['coder_state'] but in case it is not present, it will throw an error, so we use get method
        if coder_state is None:
            coder_state = CoderState(task_plan = state["task_plan"], current_step_idx = 0) # here we are storing everything in the object of CoderState class defined in states.py file
        
        steps = coder_state.task_plan.implementation_steps # it is like, object is trying to refer to the attribute of the class TaskPlan defined in states.py file
        if coder_state.current_step_idx >= len(steps):
            return {"coder_state": coder_state, "status": "DONE"}

        current_task = steps[coder_state.current_step_idx]

        existing_content = read_file.run(current_task.filepath) # 
        user_prompt = (
                        f"Task: {current_task.task_description}\n"
                        f"File Path: {current_task.filepath}\n"
                        f"Existing content: \n{existing_content}\n"
                        "Use write_file(path, content) to save the code to the specified file path.\n"
                      )
        system_prompt = coder_prompt()
        
        ## 🚨💡This line will be commented as we are not using structured output here, but using create_react_agent in future
        # response5 = llm.invoke(system_prompt + user_prompt) ‼️

        ### Writing the response which is code into a file
        coder_tools = [read_file, write_file, get_current_directory, list_files, run_cmd]
        react_agent = create_react_agent(llm, coder_tools)
        response5 = react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                         {"role": "user", "content": user_prompt}]})

        coder_state.current_step_idx += 1

        ### 🚨💡Commenting this as well as we are not returning a state anymore but we are writing code into files
        return {"coder_state" : coder_state} # the reason we use content is because response5 is of type AIMessage and we are not using structured output here ‼️
    except Exception as e:
        raise ValueError({"Coder did not return a valid response": str(e)})

## Code to create the graph and compile the agent
graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges("coder", 
                            lambda s: "END" if s.get("status") == "DONE" else "coder",
                            {END: END, "coder": "coder"})
graph.set_entry_point("planner")

agent = graph.compile()

if __name__ == "__main__":
    user_prompt = "Create a simple calculator web application"
    result = agent.invoke({"user_prompt": user_prompt},
                          {"recursion_limit": 100}) # this is used to set the maximum number of times the coder agent can call itself recursively
    print(result)