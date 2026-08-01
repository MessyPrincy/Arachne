import json
import csv
from pathlib import Path

def export_to_json(data, filepath):
    path = Path(filepath)
    with open(path, "w") as jsonfile:
        json.dump(data, jsonfile, indent=4)

def export_to_csv(data, filepath):
    path = Path(filepath)
    with open(path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)




