import json
import csv
import sqlite3
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
        sqliteConnection = sqlite3.connect(path)
        cursor = sqliteConnection.cursor()

        
        
        cursor.close()

    except sqlite3.Error as error:
        print('Error occurred -', error)

    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')



