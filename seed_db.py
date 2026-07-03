import sqlite3

def seed_database():
    print("--- 🏟️ CREATING AND SEEDING SQL DATABASE ---")
    conn = sqlite3.connect("football_hub.db")
    cursor = conn.cursor()

    # 1. Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        club TEXT NOT NULL,
        position TEXT NOT NULL,
        market_value INTEGER NOT NULL,
        contract_expiry TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        yellow_cards INTEGER DEFAULT 0,
        minutes_played INTEGER DEFAULT 0,
        FOREIGN KEY (player_id) REFERENCES players (player_id)
    )
    """)

    # Clear existing entries if re-running
    cursor.execute("DELETE FROM match_stats")
    cursor.execute("DELETE FROM players")

    # 2. Sample Data
    players_data = [
        ("Mohamed Salah", "Liverpool", "Forward", 65000000, "2027-06-30"),
        ("Darwin Nunez", "Liverpool", "Forward", 45000000, "2028-06-30"),
        ("Alexis Mac Allister", "Liverpool", "Midfielder", 70000000, "2029-06-30"),
        ("Bukayo Saka", "Arsenal", "Forward", 120000000, "2028-06-30"),
        ("Declan Rice", "Arsenal", "Midfielder", 90000000, "2029-06-30"),
        ("Erling Haaland", "Manchester City", "Forward", 180000000, "2027-06-30"),
        ("Rodri", "Manchester City", "Midfielder", 100000000, "2027-06-30")
    ]

    for p in players_data:
        cursor.execute("""
        INSERT INTO players (name, club, position, market_value, contract_expiry)
        VALUES (?, ?, ?, ?, ?)
        """, p)
        
        player_id = cursor.lastrowid
        
        # Link corresponding match statistics
        if p[0] == "Mohamed Salah":
            stats = (18, 9, 2, 2800)
        elif p[0] == "Darwin Nunez":
            stats = (12, 7, 4, 2100)
        elif p[0] == "Alexis Mac Allister":
            stats = (5, 6, 6, 2600)
        elif p[0] == "Bukayo Saka":
            stats = (16, 11, 1, 2900)
        elif p[0] == "Declan Rice":
            stats = (6, 8, 3, 3100)
        elif p[0] == "Erling Haaland":
            stats = (27, 5, 1, 2500)
        elif p[0] == "Rodri":
            stats = (8, 9, 5, 3000)
            
        cursor.execute("""
        INSERT INTO match_stats (player_id, goals, assists, yellow_cards, minutes_played)
        VALUES (?, ?, ?, ?, ?)
        """, (player_id, *stats))

    conn.commit()
    conn.close()
    print("--- ✅ SQL DATABASE SEEDED SUCCESSFULLY ('football_hub.db') ---")

if __name__ == "__main__":
    seed_database()