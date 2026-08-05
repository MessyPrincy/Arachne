import sqlite3
from pathlib import Path

def get_entries_per_scrapes(filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        sqliteConnection = sqlite3.connect(path)

        cursor = sqliteConnection.cursor()

        cursor.execute(
            "SELECT scrape_id, COUNT(*) FROM entries GROUP BY scrape_id"
        )
        
        return cursor.fetchall()

    except sqlite3.Error as error:
        print('Error occurred -', error)
    
    finally:
        if sqliteConnection:
            sqliteConnection.close()
    