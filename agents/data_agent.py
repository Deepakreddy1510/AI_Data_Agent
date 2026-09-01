import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import sql_analyst
from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from Models.schema import RouterSchema, DataAgentSchema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from langchain_groq import ChatGroq
from agents.etl_analyst import etl_analyst
from agents.sql_analyst import sql_analyst


llm = pick_llm("medium")  # Pick the appropriate LLM based on the level of the question

llm_router = llm.with_structured_output(RouterSchema)  # Create a structured output LLM for the ETL agent


# print(llm_router.invoke("I want to extract data from an API and save it as a CSV file."))


# ------------------------------------------ DATA AGENT GRAPH ----------------------------------------#

def router_node(state:DataAgentSchema):

    message = state.messages[-1].content # Get the last message from the state messages

    route_response_dict = llm_router.invoke(message).model_dump() # Get the structured output from the LLM

    route_response = route_response_dict['answer']

    return {"route_response": route_response}

# Now we need 2 more nodes, one is for SQL and other is for ETL. 
# The SQL node will be responsible for generating the SQL query and the ETL node will be responsible for generating the ETL code.


def etl_node(state:DataAgentSchema):

    message = state.messages[-1].content
    response = etl_analyst.invoke(
        {"messages":[HumanMessage(content=f"""
            {message}
        """)]}
    )
    return {
        "messages": [response["messages"][-1]]
    }


def sql_node(state:DataAgentSchema):

    message = state.messages[-1].content

    input_schema = {
        "messages": [],
        "user_question": f"{message}",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "comments": "",
        "is_safe": "No",
        "sql_query_execution_result": "",
        "final_answer": ""
    } 

    response = sql_analyst.invoke(input_schema)

    state.messages = state.messages + [response]

    return state

# Now i will simply try to create the graph
data_agent_graph = StateGraph(DataAgentSchema)

data_agent_graph.add_node("router_node", router_node)
data_agent_graph.add_node("etl_node", etl_node)
data_agent_graph.add_node("sql_node", sql_node)

data_agent_graph.add_edge(START, "router_node")

def  route_edge(state:DataAgentSchema) -> str:

    if state.route_response == "sql":
        return "sql_node"
    elif state.route_response == "etl":
        return "etl_node"
    else:
        raise ValueError("Invalid route response: {state.route_response}")

data_agent_graph.add_conditional_edges(
    "router_node", route_edge,
    {
        "sql_node": "sql_node",
        "etl_node": "etl_node"
    }
)
 

data_agent = data_agent_graph.compile()

# Display the graph in Jupyter Notebook
# optional 
from IPython.display import display, Image 
img = Image(data_agent.get_graph().draw_mermaid_png())
with open("data_agent_graph.png", "wb") as f:
    f.write(img.data)


    
if __name__ == "__main__":

    response = data_agent.invoke(
        {"messages": [HumanMessage(content="I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon'  and save it to data/extract folder in the csv folder")],
         "route_response":""}
    )

    print(response)

