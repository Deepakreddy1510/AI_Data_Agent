# 🤖 AI Data Agent

An intelligent **multi-agent data analysis system** built using **LangGraph, LangChain, Groq, PostgreSQL, and Pandas**.

The project accepts natural-language requests and automatically determines whether the task requires:

- **SQL analysis** on a PostgreSQL database, or
- **ETL operations** such as extracting data from APIs and transforming datasets.

A central **Data Agent** acts as a router and delegates each request to a specialized SQL Analyst Agent or ETL Analyst Agent.

---

## 🎯 Overview

The AI Data Agent is designed to make working with structured data easier through natural language.

Instead of manually writing SQL queries or ETL scripts, a user can provide requests such as:

```text
What are the different payment methods in the database?
```

or:

```text
Extract data from https://pokeapi.co/api/v2/pokemon
and save it in the data/extract folder as CSV.
```

The Data Agent analyzes the request, determines the appropriate workflow, and routes it to the correct specialized agent.

The project demonstrates concepts including:

- Agentic AI workflows
- Multi-agent orchestration
- LangGraph state management
- LLM tool calling
- Natural language to SQL
- SQL safety validation
- API data extraction
- LLM-generated Pandas transformations
- PostgreSQL integration
- Structured LLM outputs with Pydantic

---

# 🏗️ Architecture

The project follows a hierarchical multi-agent architecture.

```text
                         ┌─────────────────────┐
                         │      User Query     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Data Agent      │
                         │      Router         │
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐
              │   SQL Analyst   │       │   ETL Analyst   │
              │      Agent      │       │      Agent      │
              └────────┬────────┘       └────────┬────────┘
                       │                         │
              ┌────────▼────────┐       ┌────────▼────────┐
              │ Curate Question │       │   Select Tool   │
              └────────┬────────┘       └────────┬────────┘
                       │                         │
              ┌────────▼────────┐       ┌────────▼────────┐
              │ Database Schema │       │ Extract /       │
              │    Context      │       │ Transform Data  │
              └────────┬────────┘       └────────┬────────┘
                       │                         │
              ┌────────▼────────┐       ┌────────▼────────┐
              │ Generate SQL    │       │ Save Result     │
              └────────┬────────┘       └─────────────────┘
                       │
              ┌────────▼────────┐
              │ Safety Judge    │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Execute Query   │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Final Answer    │
              └─────────────────┘
```

---

# ✨ Features

## 🧠 Intelligent Query Routing

The main Data Agent determines whether a user's request belongs to:

- `sql` — database analysis
- `etl` — extraction/transformation operations

The router uses structured LLM output validated using Pydantic.

---

## 🗄️ SQL Analyst Agent

The SQL Analyst converts natural-language questions into PostgreSQL queries.

### Workflow

```text
User Question
     ↓
Curate Question
     ↓
Collect Database Schema
     ↓
Generate SQL Query
     ↓
SQL Safety Validation
     ↓
Execute Query
     ↓
Generate User-Friendly Answer
```

### Capabilities

- Natural language → SQL
- Dynamic database schema inspection
- PostgreSQL query generation
- SQL safety checking
- Automatic query execution
- User-friendly result generation
- Default result limiting for large queries

### SQL Safety

Before execution, generated SQL is passed through a safety-checking stage.

The system is designed to reject database-modifying operations such as:

```sql
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
```

Only read-oriented queries should proceed to execution.

---

# 🔄 ETL Analyst Agent

The ETL Analyst handles data extraction and transformation requests.

It uses LangChain tools that the LLM can automatically select depending on the user's request.

## Available ETL Tools

### `extract_load_tool`

Extracts data from an API and saves the result to a local data folder.

Example request:

```text
Extract data from
https://pokeapi.co/api/v2/pokemon

and save it to data/extract as CSV.
```

Example output:

```text
data/extract/extracted_data.csv
```

---

### `transform_load_tool`

Reads an existing dataset, provides sample rows to the LLM, generates appropriate Pandas transformation code, executes the transformation, and saves the result.

Example:

```text
Transform extracted_data.csv and keep only
the Pokemon named bulbasaur.
```

The LLM generates the required Pandas operations according to the user's request.

---

# 🤖 LLM Configuration

The project currently uses **Groq** as the LLM provider.

Models are selected according to task complexity.

| Level | Model |
|---|---|
| Low | `openai/gpt-oss-20b` |
| Medium | `openai/gpt-oss-120b` |
| High | `openai/gpt-oss-120b` |

The selection logic is implemented in:

```text
utils/llm_pick.py
```

This makes it possible to use smaller models for simpler operations and stronger models for more complex reasoning.

---

# 🛠️ Tech Stack

- **Python**
- **LangChain**
- **LangGraph**
- **Groq**
- **GPT-OSS**
- **Pydantic**
- **PostgreSQL**
- **Psycopg2**
- **Pandas**
- **Requests**
- **python-dotenv**

---

# 📁 Project Structure

```text
AI_Data_Agent/
│
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

---

# 📌 Main Components

## `agents/data_agent.py`

Contains the main Data Agent.

Responsibilities:

- Receive the user's request
- Classify it as SQL or ETL
- Route it to the appropriate specialized agent
- Return the result

---

## `agents/sql_analyst.py`

Contains the SQL Analyst workflow.

Responsibilities:

- Refine the user question
- Retrieve PostgreSQL schema information
- Generate SQL
- Validate SQL safety
- Execute safe queries
- Generate a natural-language answer

---

## `agents/etl_analyst.py`

Contains the ETL Agent and its LangChain tools.

Responsibilities:

- Understand ETL requests
- Select the correct tool
- Extract API data
- Generate Pandas transformations
- Execute transformations
- Report the result

---

## `Models/schema.py`

Contains the Pydantic state schemas used by LangGraph.

Main schemas include:

- `AgentSchema`
- `JudgeSchema`
- `ETLAgentSchema`
- `RouterSchema`
- `DataAgentSchema`

These schemas define the information passed between different nodes of each LangGraph workflow.

---

## `utils/database.py`

Contains reusable PostgreSQL database utilities.

It is responsible for operations such as:

- Establishing database connections
- Retrieving schema information
- Executing generated SQL queries

---

## `utils/etl_tools.py`

Contains the lower-level ETL functionality used by the ETL Agent.

Responsibilities include:

- Calling external APIs
- Converting JSON responses into Pandas DataFrames
- Saving extracted datasets
- Reading dataset samples
- Executing generated transformation code

---

## `utils/llm_pick.py`

Provides centralized LLM selection.

This makes it easy to change models without modifying every individual agent.

---

# ⚙️ Prerequisites

Before running the project, install:

- Python 3.14+
- PostgreSQL
- Git
- A Groq API key

Using a Python virtual environment is strongly recommended.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/Deepakreddy1510/AI_Data_Agent.git
cd AI_Data_Agent
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

Using `uv`:

```bash
uv sync
```

or using pip:

```bash
pip install -e .
```

---

# 🔐 Environment Configuration

Create a `.env` file in the root directory.

```env
GROQ_API_KEY=your_groq_api_key

host=localhost
port=5432
user=postgres
password=your_postgres_password
database=your_database_name
```

Do not commit the `.env` file or API keys to GitHub.

---

# 🗄️ PostgreSQL Setup

The SQL Agent requires access to a PostgreSQL database.

Database connection information is read from the environment variables:

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

which can be used for populating/setup of the sample database used while developing and testing the SQL Agent.

---

# ▶️ Running the Project

Run the complete Data Agent using:

```bash
python main.py
```

The entry point sends a natural-language question to the Data Agent.

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

---

# 💡 Example Queries

## ETL — API Extraction

```text
Extract data from the API endpoint
https://pokeapi.co/api/v2/pokemon
and save it to data/extract in CSV format.
```

The Data Agent should classify the request as:

```text
etl
```

and route it to the ETL Analyst.

---

## ETL — Data Transformation

```text
Transform the data stored in extracted_data.csv
and keep only the row for bulbasaur.
Save the transformed data in data/transform.
```

The ETL Analyst uses the dataset context and generates the required Pandas transformation.

---

## SQL — Database Question

```text
What are the different types of payment methods
available in the database?
```

The Data Agent should classify this as:

```text
sql
```

The SQL Analyst then:

1. Curates the question
2. Reads the database schema
3. Generates SQL
4. Checks whether the SQL is safe
5. Executes it
6. Converts the result into a user-friendly response

---

# 🔀 LangGraph Workflows

The repository contains generated graph diagrams for visualizing the workflows:

```text
data_agent_graph.png
etl_analyst_graph.png
sql_analyst_graph.png
```

These diagrams help illustrate how nodes and conditional edges interact inside each agent.

---

# 🧩 State Management

LangGraph state is represented using Pydantic models.

For example, the main Data Agent maintains:

```python
class DataAgentSchema(BaseModel):
    messages: Annotated[list, add]
    route_response: str
```

The `messages` field uses an additive reducer so newly generated messages can be appended while the graph executes.

The router decision is stored separately in:

```text
route_response
```

and determines which sub-agent should execute next.

---

# 🔒 Security Considerations

The project includes a dedicated LLM-based SQL safety stage intended to prevent destructive database operations from being executed.

However, this project is primarily an educational implementation.

LLM-generated SQL and Python/Pandas code should **not be executed against sensitive or production systems without additional validation and sandboxing**.

For production environments, consider adding:

- Database read-only credentials
- SQL AST validation
- Query timeouts
- Resource limits
- Sandboxed code execution
- API allowlists
- File-system restrictions
- Structured logging and monitoring

---

# 🚧 Future Improvements

Possible future improvements include:

- Add a conversational CLI or web interface
- Support additional data sources
- Add CSV/Excel database querying
- Improve SQL validation using deterministic parsing
- Add isolated/sandboxed execution for generated code
- Add persistent conversation memory
- Add automated tests
- Add retry and error-handling mechanisms
- Add observability and tracing
- Add more specialized agents
- Support additional LLM providers
- Containerize the project using Docker

---

# 📚 Learning Goals

This project was built to understand and practice:

- Agentic AI architecture
- LangGraph workflows
- Tool calling
- Multi-agent systems
- LLM routing
- Structured outputs
- SQL agents
- ETL agents
- LLM-generated code
- PostgreSQL integration
- State management in agent workflows

---

# 🙏 Acknowledgements

This project was built while learning Agentic AI and Data Agent concepts from **Ansh Lamba's Data Agent tutorial and repository**.

Tutorial:

https://youtu.be/7yOmi4IX-Rs

Original reference repository:

https://github.com/anshlambagit/AI_Data_Agent

The implementation in this repository has been adapted while learning the concepts, including changes to the LLM provider and model configuration using **Groq and GPT-OSS**.

---

# 👨‍💻 Author

**Deepak Reddy**

GitHub:

https://github.com/Deepakreddy1510

---

## ⭐ Support

If you find this project useful or interesting, consider giving the repository a ⭐.