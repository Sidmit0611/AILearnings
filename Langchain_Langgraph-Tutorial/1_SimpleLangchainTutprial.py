from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)

name = llm.invoke('Consider yourself an expert in marketing expert in hospitality business. Now I want you to \
           create only a name for me for my new restaurant which is a fine dining restaurant and serves Indian cuisine.\
                   The name should be catchy and should reflect the essence of the restaurant.')

print(name.content)