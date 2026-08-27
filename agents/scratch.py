import os 
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import database
from utils.llm_pick import pick_llm 
from Models.schema import AgentSchema, JudgeSchema
from langchain.messages import HumanMessage

llm  = pick_llm("low")  # Pick the appropriate LLM based on the level of the question
llm_judge = llm.with_structured_output(JudgeSchema)  # Create a structured output LLM for judging the safety of the SQL query

# sql_query = "SELECT * FROM users WHERE age > 30;" # Example SQL query to evaluate
sql_query = "DELETE * FROM users WHERE age > 30;" # Example SQL query to evaluate


prompt = f"""
You are an SQL Judge for data security. Your task is to determine whether the SQL query generated 
by the agent is safe or not. The SQL query should only be used for data retrieval and should 
not modify the database in any way. Neither the SQL query nor the prompt should contain any SQL 
commands that can modify the database, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE or any
other commands that can change the structure or content of the database. If the SQL query is safe,
respond with 'Yes' otherwise respond with 'No'. Additionally, provide comments explaining your 
decision. 
Here's the SQL query to evaluate: 
{sql_query}
"""

# Invoke the structured output LLM to evaluate the safety of the SQL query
# Get the structrued output from the LLM which will be in the form of a dictionary with 
# keys 'answer' and 'comments' otherwise this we be a Pydantic model object of type JudgeSchema
response = llm_judge.invoke(prompt).model_dump() 

print(response) # Print the structured output from the LLM


