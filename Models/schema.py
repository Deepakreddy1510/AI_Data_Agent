# schema.py means what data the graph carries.

from pydantic import BaseModel, Field
from typing import Annotated, Any, Literal
from operator import add

# Annotated lets you attach metadata to types. 

# SQL Graph State
class AgentSchema(BaseModel):
    messages : Annotated[list,add] = Field(default_factory=list)
    agent_instructions : str = ""
    user_question : str = ""
    curated_ques : str = ""
    prompt_query_context : str = ""
    generated_sql_query : str = ""
    is_safe : Literal["Yes","No"] = "No"
    comments : str = ""
    sql_query_execution_result : Any = ""
    final_answer : str = ""
    database_url : str = ""
    conversation_history : list[dict[str,str]] = Field(default_factory=list)
    retry_count : int = 0
    tables_used : list[str] = Field(default_factory=list)


class JudgeSchema(BaseModel):
    answer : Literal["Yes","No"]
    comments : str 


class ETLAgentSchema(BaseModel):
    messages : Annotated[list,add] = Field(default_factory=list)
    agent_instructions : str = ""

class RouterSchema(BaseModel):
    answer: Literal["sql","etl"] 
    comments: str = ""

class DataAgentSchema(BaseModel):
    messages : Annotated[list,add] = Field(default_factory=list)
    route_response : str = ""
    database_url : str = ""
    agent_instructions : str = "" # This stores the instructions entered in the frontend for the data agent to follow.
    conversation_history : list[dict[str,str]] = Field(default_factory=list)
    agent_result : dict[str,Any] = Field(default_factory=dict)