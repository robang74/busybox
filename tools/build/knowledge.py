import json
import pathlib
import time

DB = pathlib.Path(__file__).parent / "history.json"


def load():

    if not DB.exists():
        return {"runs": []}

    return json.loads(DB.read_text())


def save(data):
    DB.write_text(json.dumps(data, indent=2))


def record(build_type, success, log):

    data = load()

    data["runs"].append({
        "time": int(time.time()),
        "type": build_type,
        "success": success,
        "log_tail": log[-2000:]
    })

    save(data)
