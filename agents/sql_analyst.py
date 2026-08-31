import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.database import DatabaseUtil
from utils.llm_pick import pick_llm
from Models.schema import AgentSchema, JudgeSchema
from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()


def _db_config() -> dict:
    """Match utils/feed_db.py: .env uses `database`, not `dbname`."""
    if "port" not in os.environ:
        os.environ["port"] = "5432"
    return {
        "host": os.environ["host"],
        "port": int(os.environ["port"]),
        "user": os.environ["user"],
        "password": os.environ["password"],
        "database": os.environ["database"],
    }


def _extract_sql(raw_sql: str) -> str:
    """LLMs often wrap SQL in markdown fences; strip those before execution."""
    text = (raw_sql or "").strip()
    fenced = re.search(r"```(?:sql)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    return text


def _parse_judge_text(raw: str) -> dict:
    """Parse Yes/No + comments from JSON or markdown (gpt-oss often ignores tools)."""
    text = (raw or "").strip()
    json_blob = re.search(r"\{.*\}", text, re.DOTALL)
    if json_blob:
        try:
            data = json.loads(json_blob.group())
            answer = str(data.get("answer", "")).strip()
            if answer.lower() in ("yes", "no"):
                return {
                    "answer": "Yes" if answer.lower() == "yes" else "No",
                    "comments": str(data.get("comments", "")).strip(),
                }
        except json.JSONDecodeError:
            pass

    match = re.search(r"Answer[:\*]*\s*(Yes|No)", text, re.IGNORECASE)
    if match:
        comments_match = re.search(r"Comments[:\*]*\s*(.*)", text, re.IGNORECASE | re.DOTALL)
        comments = comments_match.group(1).strip() if comments_match else text
        return {
            "answer": "Yes" if match.group(1).lower() == "yes" else "No",
            "comments": comments,
        }

    raise ValueError(f"Could not parse SQL-safety judge output: {text[:500]}")

# --------------------------------------- AI Agent Code----------------------------------------

def curate_question(state: AgentSchema) -> str:

    user_question = state.user_question # Bcoz this is a Pydantic model object, we can access the attributes directly

    llm = pick_llm("low")  # Pick the appropriate LLM based on the level of the question

    response = llm.invoke(f"Curate the following question: {user_question}").content

    state.curated_ques = response # Update the state with the curated question
    state.messages = state.messages + [HumanMessage(content=f"{response}")] # Append the curated question to the messages list
    return state


def prompt_query_context(state: AgentSchema) -> str:

    curated_question = state.curated_ques

    obj = DatabaseUtil(_db_config())

    schema_info = obj.schema_details("public")  # Fetch schema details for the 'public' schema

    # Constructing the prompt query for the agent to generate the SQL query
    prompt = f"""
    You are an SQL analyst agent. Your task is to convert the user's natural language 
    query into Postgres SQL query that can be executed on the database. You are provided 
    with the user's original query and the schema details of the database, including
    table names, column names, data types, and sample data for each table so that 
    you can understand the structure of the database and generate an accurate SQL query.
    Unless user explicitly asks for specific number of rows, always limit the output to 10 rows.
    Note - Just generate the SQL query without any explanation or additional text because
    this query will be executed directly on the database. So, the output should be SQL
    ready to be executed without any modifications.  
    
    User's Original Query: {curated_question}

    Database Schema Details:
    {schema_info}
    
    """    

    state.prompt_query_context = prompt

    return state


# Generate SQL Query Node
def generate_sql(state: AgentSchema) -> AgentSchema:
    prompt = state.prompt_query_context

    # this prompt will go to the llm and i will create a medium level llm
    llm = pick_llm("medium")
    generated_sql_query = llm.invoke(prompt).content  # Generate the SQL query using the LLM

    state.generated_sql_query = _extract_sql(generated_sql_query)

    return state



# Is Safe Node
def is_safe_sql(state: AgentSchema) -> str:

    sql_query = state.generated_sql_query

    llm = pick_llm("medium")

    # gpt-oss on Groq often ignores tool/schema calling; ask for JSON and parse it.
    prompt = f"""
    You are an SQL Judge for data security. Your task is to determine whether the SQL query generated
    by the agent is safe or not. The SQL query should only be used for data retrieval and should
    not modify the database in any way. Neither the SQL query nor the prompt should contain any SQL
    commands that can modify the database, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE or any
    other commands that can change the structure or content of the database.

    Return ONLY a JSON object with exactly these keys:
    - "answer": "Yes" if the query is read-only/safe, otherwise "No"
    - "comments": a short explanation of your decision

    SQL query to evaluate:
    {sql_query}
    """

    raw = llm.invoke(prompt).content
    response = JudgeSchema.model_validate(_parse_judge_text(raw)).model_dump()

    state.is_safe_sql_response = response['answer']
    state.comments = response['comments']

    return state

# Canceled SQL Query Node
def canceled_sql(state: AgentSchema) -> AgentSchema:

    comments = state.comments

    state.final_answer = f"The SQL query was deemed unsafe to execute. The reason provided by the judge is: {comments}. Therefore, the SQL query will not be executed, and no results will be returned."
    state.messages = state.messages + [AIMessage(content=f"{state.final_answer}")] # Append the final answer to the messages list

    return state


# Execute SQL Query Node
def execute_sql(state: AgentSchema) -> AgentSchema:

    sql_query = _extract_sql(state.generated_sql_query)
    state.generated_sql_query = sql_query

    obj = DatabaseUtil(_db_config())

    execution_result = obj.execute_query(sql_query)  # Execute the SQL query on the database

    state.sql_query_execution_result = execution_result # Update the state with the execution result
    state.final_answer = f"The SQL query was executed successfully. The results are: {execution_result}"

    return state

# Represent the final answer Node 
def represent_final_answer(state: AgentSchema) -> str:
    executed_result = state.sql_query_execution_result
    curated_question = state.curated_ques 

    llm = pick_llm("low")  # Pick the appropriate LLM based on the level of the question

    prompt = f"""
    You are an SQL analyst agent. Your task is to represent the final answer to the user based 
    on the execution result of the SQL query and the user's original question. The final answer 
    should be concise, clear, and directly address the user's query. Avoid including any SQL code
    or technical details in the final answer. The final answer should be in a user-friendly format
    that is easy to understand. If the execution result is empty or does not provide a clear answer
    to the user's question, explain this in the final answer and provide any relevant information that may help the user understand the situation.\n
    Here is the execution result of the SQL query: {executed_result} \n
    Here is the user's original Question: {curated_question}
    """

    llm_response = llm.invoke(prompt).content # Generate the final answer from the LLM

    state.final_answer = llm_response # Update the state with the final answer
    state.messages = state.messages + [AIMessage(content=f"{llm_response}")] # Append the final answer to the messages list

    return state


# -------------------------------------------Graph Building-------------------------------------------

sql_agent_graph = StateGraph(AgentSchema)

# Nodes
# Make sure use same function names as defined above for the nodes
sql_agent_graph.add_node("curated_ques", curate_question)
sql_agent_graph.add_node(prompt_query_context, name="prompt_query_context")
sql_agent_graph.add_node(generate_sql, name="generate_sql")
sql_agent_graph.add_node(is_safe_sql, name="is_safe_sql")
sql_agent_graph.add_node(canceled_sql, name="canceled_sql")
sql_agent_graph.add_node(execute_sql, name="execute_sql")
sql_agent_graph.add_node(represent_final_answer, name="represent_final_answer")

# The above nodes are independent nodes which are not connected to each other. Now we will connect them based on the flow of the agent.

#edges
sql_agent_graph.add_edge(START, "curated_ques")
sql_agent_graph.add_edge("curated_ques", "prompt_query_context")
sql_agent_graph.add_edge("prompt_query_context", "generate_sql")
sql_agent_graph.add_edge("generate_sql", "is_safe_sql")

# I have two edges so here comes the concept of conditional edges. 
# Based on the output of the is_safe_sql node, we will decide which edge to take next. 
# If the SQL query is safe, we will execute it, otherwise we will cancel it.

# Conditional Edge Function
def is_safe_sql_edge(state: AgentSchema) -> str:
    is_safe = state.is_safe_sql_response

    if is_safe.lower() == "yes":
        return "execute_sql"
    else:
        return "canceled_sql"   

sql_agent_graph.add_conditional_edges(
    "is_safe_sql",
    is_safe_sql_edge,
    {"execute_sql": "execute_sql", "canceled_sql": "canceled_sql"},
)

sql_agent_graph.add_edge("canceled_sql", END)
sql_agent_graph.add_edge("execute_sql", "represent_final_answer")
sql_agent_graph.add_edge("represent_final_answer", END)



# Compile the graph
sql_analyst = sql_agent_graph.compile()

# We want to run it only when we run this file directly, not when we import it as a module.
# So, we will use the below condition.
if __name__ == "__main__":
    # Compile the Graph

    # Display the graph in Jupyter Notebook
    # optional 
    # from IPython.display import display, Image
    # img = Image(sql_analyst.get_graph().draw_mermaid_png())
    # with open("sql_analyst_graph.png", "wb") as f:
    #     f.write(img.data)

    # Once we have the image ready then I can invoke this function but before invoking i need to have 
    # atleast one object so i simply say input schema and prepare in format of dictionary for 
    # our Pydantic model but we can't send it directly to the pydantic model because it will not
    # accept the dictionary directly, we need to convert it into a Pydantic model object first.
    # So , we will create a dictionary with the required fields and then convert it into a Pydantic model object using the AgentSchema class.
    input_schema = {
        "messages": [],
        "user_question": "What are the different types of payment methods we have in our database",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "comments": "",
        "is_safe_sql_response": "No",
        "sql_query_execution_result": "",
        "final_answer": ""
    } 

    # Execute the graph 
    sql_analyst_response = sql_analyst.invoke(input_schema)
    print(sql_analyst_response['messages']) # Print the final output of the graph execution
    print("******************************")

    print(sql_analyst_response['generated_sql_query']) # Print the generated SQL query

    print("******************************")

    print(sql_analyst_response['sql_query_execution_result']) # Print the result of executing the SQL query

    print("******************************")

    print(sql_analyst_response['prompt_query_context']) # Print the prompt query context


    # sql_analyst_response = sql_analyst.invoke(input_schema)
    # print(sql_analyst_response.get("final_answer", sql_analyst_response))











    