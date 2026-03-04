import json, pathlib, time

DB = pathlib.Path(__file__).parent / "db.json"

def load():
    if not DB.exists():
        return {"entries": []}
    return json.loads(DB.read_text())

def save(data):
    DB.write_text(json.dumps(data, indent=2))

def store_failure(build_type, log):
    data = load()
    data["entries"].append({
        "time": int(time.time()),
        "type": build_type,
        "log": log[-2000:],
        "patch": None
    })
    save(data)

def store_fix(patch):
    data = load()
    if data["entries"]:
        data["entries"][-1]["patch"] = patch
    save(data)

def search_memory(log):
    data = load()
    for entry in reversed(data["entries"]):
        if entry["log"][:120] in log:
            return entry.get("patch")
    return None
