import sqlite3
from langchain_core.tools import tool

@tool
def query_football_analytics_db(sql_query: str) -> str:
    """
    Executes a raw SQLite query against the local football hub database.
    Use this tool to resolve dynamic player stats, goals, assists, yellow cards, 
    market values, clubs, positions, or contract expirations.
    
    The database contains two tables:
    1. 'players' (player_id, name, club, position, market_value, contract_expiry)
    2. 'match_stats' (stat_id, player_id, goals, assists, yellow_cards, minutes_played)
    
    Input must be a valid, clean SQLite statement.
    """
    try:
        conn = sqlite3.connect("football_hub.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        if not rows:
            return "No matching database records found."
            
        # Format columns dynamically for the model's text context
        colnames = [description[0] for description in cursor.description]
        result_strings = []
        for row in rows:
            row_dict = dict(zip(colnames, row))
            result_strings.append(str(row_dict))
            
        conn.close()
        return "\n".join(result_strings)
    except Exception as e:
        return f"SQL Error encountered during execution: {str(e)}"