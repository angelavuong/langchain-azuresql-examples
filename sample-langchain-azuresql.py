# This is a test script from 
# https://devblogs.microsoft.com/azure-sql/building-your-own-db-copilot-for-azure-sql-with-azure-openai-gpt-4/
# Ask the LLM on data that's stored in Azure SQL 

import pyodbc
import os
from dotenv import load_dotenv
from langchain.agents import create_sql_agent
from langchain_openai import AzureChatOpenAI
from langchain.sql_database import SQLDatabase

load_dotenv()

# connect to the Azure SQL database

from sqlalchemy import create_engine

connectionString=os.environ["py-connectionString"]
db_engine = create_engine(connectionString)
db = SQLDatabase(db_engine, view_support=True, schema="dbo")

# test the connection
print(db.dialect)
print(db.get_usable_table_names())

# reference to AOAI LLM

azurellm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=4000
)

# Create system message for LLM 
from langchain.prompts.chat import ChatPromptTemplate

system_message = ChatPromptTemplate.from_messages( 
    [
        ("system", 
         """
         You are a helpful AI assistant expert in querying SQL Database to find answers to user's question clients information.
         """
         ),
        ("user", "{question}\n ai: "),
    ]
)
# Create agent to chat with Azure SQL DB 

from langchain.agents.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=azurellm)

from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType

agent_executor = create_sql_agent(
    llm=azurellm,
    toolkit=toolkit,
    prompt_template=system_message,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

agent_executor.invoke("How many clients are over 30?")
