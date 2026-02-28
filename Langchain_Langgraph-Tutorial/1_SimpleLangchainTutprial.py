from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
load_dotenv()

### Loading the LLM
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)

### Output parser (Converts AI Message to String)
output_parser = StrOutputParser()

## invoking it directly ---------------------------------------------------------------------------------------------------------------------------------
name = llm.invoke('Consider yourself an expert in marketing expert in hospitality business. Now I want you to \
           create only a name for me for my new restaurant which is a fine dining restaurant and serves Indian cuisine.\
                   The name should be catchy and should reflect the essence of the restaurant.')
print(name.content)
# ---------------------------------------------------------------------------------------------------------------------------------

### Select the cuisine here, declaring here because name.chain at line 33 is using it,
### Other wise, we can define it only once as well, at the bottom and pass it to the entire pipeline, but for the sake of simplicity, we are defining it here.
cuisine = "Indian"

# -------------------------
# Step 1: Generate Restaurant Name
# -------------------------
prompt = PromptTemplate(
    input_variables=["cuisine"],
    template="I want to open a restaurant for {cuisine} cuisine. Can you suggest a catchy name for it?"
)

name_chain = prompt | llm | output_parser
response = name_chain.invoke({"cuisine": cuisine})
print(response) 

# -------------------------
# Step 2: Generate Menu using Restaurant Name
# -------------------------
menu_prompt = PromptTemplate(
    input_variables=["restaurant_name", "cuisine"],
    template="Given the restaurant name '{restaurant_name}' and it serves '{cuisine}' cuisine, \
          Create a premium fine dine menu with 5 dishes \
          - 3 Starters \
          - 3 Main Courses \
          - 2 Desserts"
)

menu_chain =  menu_prompt | llm | output_parser
menu_response = menu_chain.invoke({"restaurant_name": response, "cuisine": cuisine})
print(menu_response)


# -------------------------
# Step 3: Sequential Chain (IMPORTANT PART)
# -------------------------

sequential_chain = (
    {
        "restaurant_name": name_chain,   # Output of name_chain
        "cuisine": RunnablePassthrough() # Pass cuisine as-is, A runnable that returns whatever input it receives.
    }
    | menu_chain
)


# Run entire pipeline
result = sequential_chain.invoke(cuisine) # this is the input for the entire pipeline, it will be passed to the RunnablePassthrough and the output of name_chain will be passed to menu_chain

print(result)