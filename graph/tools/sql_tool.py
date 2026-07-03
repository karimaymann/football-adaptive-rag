import sqlite3
from langchain_core.tools import tool

@tool
def query_football_analytics_db(sql_query: str) -> str:
    """
    Executes an analytic SQLite query against the football database to retrieve structured data.
    Input must be a valid, executable SQL query string.
    
    Database Schema:
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
    try:
        conn = sqlite3.connect("football_hub.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Extract column names to format cleanly
        colnames = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for r in rows:
            results.append(str(dict(zip(colnames, r))))
            
        return "\n".join(results) if results else "No matching statistical entries found."
    except Exception as e:
        return f"Database execution error: {e}"