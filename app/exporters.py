import json
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

def export_to_json(data, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as jsonfile:
        json.dump(data, jsonfile, indent=4)

def export_to_csv(data, filepath):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def export_to_db(data, filepath, url):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Connect to db
        sqliteConnection = sqlite3.connect(path)
        # Need to turn on foreign keys since they are OFF by default
        sqliteConnection.execute("PRAGMA foreign_keys = ON")
        # Need a cursor to execute
        cursor = sqliteConnection.cursor()

        # Create the main table if it doesn't exist already
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS data (" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "entry_id INTEGER NOT NULL," \
            "key TEXT NOT NULL," \
            "value TEXT NOT NULL," \
            "FOREIGN KEY (entry_id) REFERENCES entries(id))"
        )

        # Create the scrapes table which has information about the source_url and when the scrape was done
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS scrapes (" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "source_url TEXT NOT NULL," \
            "scraped_at TEXT NOT NULL)"
        )

        # Create the entry table to remember each entry, easier for loading data in the web interface
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS entries (" \
            "id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "scrape_id INTEGER NOT NULL," \
            "FOREIGN KEY (scrape_id) REFERENCES scrapes(id))"
        )

        # Insert information about the scrape and get the scrape_id
        cursor.execute(
            "INSERT INTO scrapes (source_url, scraped_at) VALUES (?, ?)", 
            (url, datetime.now().isoformat())
        )
        scrape_id = cursor.lastrowid

        for entry in data:
            # Insert information about the entry and get the entry_id
            cursor.execute(
                "INSERT INTO entries (scrape_id) VALUES (?)",
                (scrape_id,)
            )
            entry_id = cursor.lastrowid
            for key, value in entry.items():
                # Save the key and the value with each entry
                cursor.execute(
                    "INSERT INTO data (entry_id, key, value) VALUES (?, ?, ?)",
                    (entry_id, key, value)
                )

        # Commit the changes to the database and close the cursor
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print('Error occurred -', error)

    finally:
        if sqliteConnection:
            sqliteConnection.close()



