from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

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

user_prompt = "Create a simple calculator web application"

prompt = f"""
You are a Planner Agent. Convert the user prompt into a COMPLETE engineering project plan
User Request: {user_prompt}
"""

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

response1 = llm.invoke("Who invented Kriya Yoga?. Answer in 1 sentence")
print(response1)

response2 = llm.with_structured_output(Schema).invoke("Extract Price and EPS from this report \n" \
                      "The price of the stock is $150 and the EPS is $5.25.")
print(response2.price)
print(response2.eps)

response3 = llm.with_structured_output(Plan).invoke(prompt)
print(response3.name)
print(response3.description)
print(response3.techstack)
print(response3.features)
for file in response3.files:
    print(f"File Path: {file.path}, Purpose: {file.purpose}")

