from pydantic import BaseModel, Field

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