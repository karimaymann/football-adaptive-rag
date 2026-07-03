import sqlite3
from typing import Any, Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from graph.state import GraphState

DB_SCHEMA = """
Table: players
- player_id (INTEGER, Primary Key)
- name (TEXT)
- club (TEXT)
- position (TEXT)
- market_value (INTEGER)
- contract_expiry (TEXT)

Table: match_stats
- stat_id (INTEGER, Primary Key)
- player_id (INTEGER, Foreign Key referencing players.player_id)
- goals (INTEGER)
- assists (INTEGER)
- yellow_cards (INTEGER)
- minutes_played (INTEGER)
"""

class SQLQueryGenerator(BaseModel):
    """Structured container for the compiled SQL command."""
    query: str = Field(description="The executable SQLite query string matching the request criteria.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_sql_generator = llm.with_structured_output(SQLQueryGenerator)

sql_prompt = ChatPromptTemplate.from_messages([
    ("system", f"You are a database engineer. Based on the user's question, write a valid SQLite query. "
               f"Return ONLY the executable query text inside the schema object format. Do not add markdown backticks.\n\nSchema:\n{DB_SCHEMA}"),
    ("human", "{question}")
])

sql_chain = sql_prompt | structured_sql_generator

def sql_node(state: GraphState) -> Dict[str, Any]:
    print("---NODE: COMPILING AND EXECUTING STRUCTURED SQL QUERY---")
    question = state["question"]
    
    # 1. Compile the query text
    generated_sql_obj = sql_chain.invoke({"question": question})
    sql_command = generated_sql_obj.query
    print(f"  -> Generated SQL Command: {sql_command}")
    
    # 2. Execute natively against local SQLite database
    try:
        conn = sqlite3.connect("football_hub.db")
        cursor = conn.cursor()
        cursor.execute(sql_command)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        conn.close()
        
        result_strings = []
        for r in rows:
            row_dict = dict(zip(colnames, r))
            result_strings.append(str(row_dict))
            
        data_context = "\n".join(result_strings) if result_strings else "No matching rows found in the analytics ledger."
        
    except Exception as e:
        print(f"  -> SQL Execution Error: {e}")
        data_context = f"Database tracking error during lookup: {e}"

    db_document = Document(page_content=data_context, metadata={"source": "sql_database"})
    
    return {"documents": [db_document], "question": question}