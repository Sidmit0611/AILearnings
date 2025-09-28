def planner_prompt(user_prompt: str) -> str:
    PLANNER_PROMPT = f"""
    You are a Planner Agent. Convert the user prompt into a COMPLETE engineering project plan
    User Request: {user_prompt}
        """
    return PLANNER_PROMPT