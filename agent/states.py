from pydantic import BaseModel, Field, ConfigDict

class Schema(BaseModel):
    price: float
    eps: float

class File(BaseModel):
    path: str = Field(description="Path to the file that needs to be created")
    purpose: str = Field(description="Purpose of the file, example: main application logic, data pocessing module, UI component etc.")
    
class Plan(BaseModel):
    name: str = Field(description="Name of the app to be built")
    description: str = Field(description="One line description of the app")
    techstack: list[str] = Field(description="List of technologies to be used, e.g. React, Flask, Python, ReactJS, JavaScript etc.")
    features: list[str] = Field(description="List of features a user should have, e.g. Login, Signup, User Profile, User Authentication, Dashboard etc.")
    files: list[File] = Field(description="List of files to be created with a Path and Purpose of the file")

class ImplementationTask(BaseModel):
    filepath: str = Field(description="Path to the file where this task will be implemented")
    task_description: str = Field(description="Detailed description of the implementation task")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the project. Each step should be self-contained and explicitly detailed, but also carry forward the context of previous steps.")
    model_config = ConfigDict(extra = 'allow')