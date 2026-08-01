import json
from pathlib import Path

def export_to_json(data, filepath):
    path = Path(filepath)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)



