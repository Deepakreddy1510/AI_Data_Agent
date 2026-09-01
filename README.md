# AI Data Agent

An AI-powered multi-agent system for working with structured data using natural language.

The project uses **LangGraph, LangChain, Groq, GPT-OSS, PostgreSQL, and Pandas** to route user requests to specialized agents for SQL analysis or ETL operations.

## Overview

AI Data Agent allows users to interact with databases and data-processing workflows using natural-language instructions.

For example, a user can ask:

```text
What are the different payment methods available in the database?
```

or:

```text
Extract data from https://pokeapi.co/api/v2/pokemon
and save it in the data/extract folder as CSV.
```

The main Data Agent analyzes the request and routes it to one of two specialized agents:

* SQL Analyst Agent
* ETL Analyst Agent

This project demonstrates concepts such as:

* Agentic AI
* Multi-agent workflows
* LangGraph orchestration
* LLM tool calling
* Natural language to SQL
* SQL safety validation
* API data extraction
* Data transformation using Pandas
* Structured outputs using Pydantic
* PostgreSQL integration

## Architecture

The system follows a router-based multi-agent architecture.

```text
                        User Query
                            |
                            v
                     +-------------+
                     | Data Agent  |
                     |   Router    |
                     +------+------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
        +---------------+       +---------------+
        | SQL Analyst   |       | ETL Analyst   |
        |    Agent      |       |    Agent      |
        +-------+-------+       +-------+-------+
                |                       |
                v                       v
        Curate Question            Select Tool
                |                       |
                v                       v
        Database Context          Extract / Transform
                |                       |
                v                       v
          Generate SQL              Save Result
                |
                v
          Safety Check
                |
                v
          Execute Query
                |
                v
          Final Answer
```

The workflow is:

```text
User Input
    |
    v
Data Agent Router
    |
    +---- SQL Request ----> SQL Analyst Agent
    |
    +---- ETL Request ----> ETL Analyst Agent
```

## Features

### Intelligent Query Routing

The Data Agent automatically identifies whether the user's request is related to:

```text
sql
```

or:

```text
etl
```

The router uses structured LLM output validated using Pydantic.

### SQL Analyst Agent

The SQL Analyst Agent converts natural-language questions into PostgreSQL queries.

Its workflow includes:

1. Curating the user's question
2. Retrieving database schema information
3. Building database context for the LLM
4. Generating a SQL query
5. Validating SQL safety
6. Executing safe queries
7. Converting the result into a user-friendly response

Example:

```text
What are the different types of payment methods in the database?
```

The agent can generate the appropriate SQL query, validate it, execute it, and return the results.

### SQL Safety Validation

Before executing a generated query, the SQL Agent checks whether the query is safe.

The safety layer is designed to prevent destructive operations such as:

```sql
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
```

The intended workflow allows read-oriented SQL queries to continue while unsafe queries are rejected.

### ETL Analyst Agent

The ETL Analyst Agent handles extraction and transformation tasks.

It currently provides tools for:

* Extracting data from APIs
* Saving extracted data locally
* Reading dataset context
* Generating Pandas transformation code
* Executing generated transformations
* Saving transformed results

### API Data Extraction

Example request:

```text
Extract data from the API endpoint
https://pokeapi.co/api/v2/pokemon
and save it to data/extract in CSV format.
```

The ETL Agent selects the extraction tool and saves the result as:

```text
data/extract/extracted_data.csv
```

### Data Transformation

The ETL Agent can also transform existing data.

Example:

```text
Transform the extracted Pokemon data and keep only
the row containing bulbasaur.
```

The agent provides the data context to the LLM, generates Pandas code based on the request, and executes the transformation.

## LLM Configuration

The project currently uses **Groq** as the LLM provider.

The models are selected according to task complexity.

| Level  | Model                 |
| ------ | --------------------- |
| Low    | `openai/gpt-oss-20b`  |
| Medium | `openai/gpt-oss-120b` |
| High   | `openai/gpt-oss-120b` |

The model selection logic is implemented in:

```text
utils/llm_pick.py
```

This allows different models to be selected without changing the logic inside individual agents.

## Tech Stack

The main technologies used in this project are:

* Python
* LangChain
* LangGraph
* Groq
* GPT-OSS
* PostgreSQL
* Psycopg2
* Pandas
* Pydantic
* Requests
* python-dotenv

## Project Structure

```text
AI_Data_Agent/
|
├── agents/
│   ├── data_agent.py
│   ├── etl_analyst.py
│   └── sql_analyst.py
│
├── Models/
│   └── schema.py
│
├── utils/
│   ├── database.py
│   ├── etl_tools.py
│   ├── feed_db.py
│   └── llm_pick.py
│
├── data/
│   ├── extract/
│   └── transform/
│
├── data_agent_graph.png
├── etl_analyst_graph.png
├── sql_analyst_graph.png
│
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Main Components

### Data Agent

File:

```text
agents/data_agent.py
```

The Data Agent acts as the main router.

Its responsibilities include:

* Receiving the user's query
* Understanding the request
* Classifying it as SQL or ETL
* Routing it to the appropriate agent
* Returning the result

### SQL Analyst

File:

```text
agents/sql_analyst.py
```

The SQL Analyst handles natural-language database questions.

Its responsibilities include:

* Question curation
* Database schema retrieval
* SQL generation
* SQL safety checking
* SQL execution
* Final answer generation

### ETL Analyst

File:

```text
agents/etl_analyst.py
```

The ETL Analyst handles extraction and transformation requests.

Its responsibilities include:

* Understanding ETL instructions
* Selecting the correct tool
* Extracting API data
* Generating Pandas transformations
* Executing transformations
* Returning the result

### Schemas

File:

```text
Models/schema.py
```

This file contains the Pydantic models used for LangGraph state management.

The main schemas include:

```text
AgentSchema
JudgeSchema
ETLAgentSchema
RouterSchema
DataAgentSchema
```

### Database Utilities

File:

```text
utils/database.py
```

This module contains reusable PostgreSQL functionality such as:

* Database connection management
* Retrieving schema details
* Executing SQL queries

### ETL Utilities

File:

```text
utils/etl_tools.py
```

This module contains the lower-level ETL functionality used by the ETL Agent.

It handles:

* API requests
* JSON normalization
* Pandas DataFrames
* Dataset loading
* File creation
* Transformation code execution

### LLM Selection

File:

```text
utils/llm_pick.py
```

The `pick_llm()` function selects a Groq-hosted GPT-OSS model based on the requested complexity level.

## Prerequisites

Before running the project, make sure you have:

* Python 3.14+
* PostgreSQL
* Git
* Groq API key

Using a virtual environment is recommended.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Deepakreddy1510/AI_Data_Agent.git
cd AI_Data_Agent
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Using `uv`:

```bash
uv sync
```

or:

```bash
pip install -e .
```

## Environment Configuration

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key

host=localhost
port=5432
user=postgres
password=your_postgres_password
database=your_database_name
```

Do not commit your `.env` file or API keys to GitHub.

## PostgreSQL Setup

The SQL Analyst requires access to a PostgreSQL database.

The application reads database configuration from the following environment variables:

```text
host
port
user
password
database
```

The project also contains:

```text
utils/feed_db.py
```

which is used for setting up and populating the sample database used during development.

## Running the Project

Run the main Data Agent using:

```bash
python main.py
```

Example:

```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

response = data_agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="""
                Extract the data from the API endpoint
                'https://pokeapi.co/api/v2/pokemon'
                and save it to data/extract in CSV format.
                """
            )
        ],
        "route_response": ""
    }
)

print(response)
```

## Example Queries

### API Extraction

```text
Extract data from the API endpoint
https://pokeapi.co/api/v2/pokemon
and save it to data/extract in CSV format.
```

Expected route:

```text
etl
```

The ETL Agent extracts the data and saves it locally.

### Data Transformation

```text
Transform the data stored in extracted_data.csv
and keep only the row for bulbasaur.

Save the transformed data in data/transform.
```

The ETL Agent generates and executes the required Pandas transformation.

### Database Query

```text
What are the different types of payment methods
available in the database?
```

Expected route:

```text
sql
```

The SQL Analyst then performs the following workflow:

```text
Question
   |
   v
Question Curation
   |
   v
Database Schema
   |
   v
SQL Generation
   |
   v
Safety Validation
   |
   v
SQL Execution
   |
   v
Final Answer
```

## LangGraph Workflows

The repository contains generated workflow diagrams:

```text
data_agent_graph.png
etl_analyst_graph.png
sql_analyst_graph.png
```

These diagrams show how the nodes and conditional edges are connected inside each LangGraph workflow.

## State Management

The project uses Pydantic models to represent the state passed between LangGraph nodes.

For example, the main Data Agent state contains:

```python
class DataAgentSchema(BaseModel):
    messages: Annotated[list, add]
    route_response: str
```

The message state is used to maintain the agent conversation while the router decision determines which specialized agent should handle the request.

## Security Considerations

The SQL workflow contains an LLM-based validation step designed to detect potentially destructive SQL queries before execution.

The ETL workflow can also generate and execute Python/Pandas code dynamically.

Because generated code is executed programmatically, this project should currently be treated as an educational and development project rather than a production-ready system.

For production use, additional protections should be added, such as:

* Read-only database credentials
* Deterministic SQL validation
* SQL parsing using an AST
* Query timeouts
* Sandboxed Python execution
* File-system restrictions
* Resource limits
* API allowlists
* Logging and monitoring

## Future Improvements

Possible improvements include:

* Conversational CLI
* Web-based user interface
* Persistent conversation memory
* Additional data sources
* More ETL tools
* Excel file support
* Improved SQL validation
* Sandboxed generated-code execution
* Automated tests
* Retry and error handling
* LangSmith or other tracing support
* Docker support
* Additional LLM providers
* Additional specialized agents

## Learning Goals

This project was developed to learn and practice:

* Agentic AI
* LangGraph
* LangChain
* Multi-agent systems
* LLM routing
* Tool calling
* Structured outputs
* SQL agents
* ETL agents
* PostgreSQL integration
* Pandas transformations
* LangGraph state management

## Author

**Deepak Reddy**

GitHub: [Deepakreddy1510](https://github.com/Deepakreddy1510)
