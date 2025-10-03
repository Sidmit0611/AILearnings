def planner_prompt(user_prompt: str) -> str:
    PLANNER_PROMPT = f"""
    You are a Planner Agent. Convert the user prompt into a complete engineering project plan
    User Request: {user_prompt}
        """
    return PLANNER_PROMPT

def architect_prompt(plan: str) -> str:
    ARCHITECT_PROMPT = f"""
    You are an Architect Agent. Given the project plan, break it down into explicit engineering tasks and create a file structure for the project.

    Rules:
    - For each FILE in the plan, create one or more IMPLEMENTATION TASKS.
    - In each task description:
        * Specify exactly what to implement.
        * Name the variables, functions, classes and components to be defined.
        * Mention how this task depends on or will be used by previous tasks.
        * Include integration details: imports, expected function signatures, data flow etc.
    - Order tasks so that dependencies are implemented before they are used.
    - Each step must be SELF-CONTAINED and EXPLICITLY DETAILED but also carry FORWARD the CONTEXT of previous steps.
    - Use the exact FILE PATHS from the plan when specifying where to implement each task.
    - Do NOT create tasks for files NOT in the plan.
    - Do NOT create tasks for non-implementation activities like testing, documentation, deployment etc.
    - Do NOT create tasks for setting up the development environment, installing dependencies or configuring tools.
    - Do NOT create tasks for non-technical activities like project management, meetings, research etc
    Project Plan: {plan}
        """
    return ARCHITECT_PROMPT