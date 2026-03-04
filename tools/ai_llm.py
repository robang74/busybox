import os, requests
from ai_models.loader import call_local_model
from ai_models.config import PROVIDER, LOCAL_MODEL

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

def call_openai(prompt):
    key = os.environ["OPENAI_API_KEY"]
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENAI_MODEL,
            "messages":[{"role":"user","content":prompt}],
            "temperature":0.2
        },
        timeout=180
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def call_llm(prompt):
    if PROVIDER == "local":
        return call_local_model(prompt, LOCAL_MODEL)
    return call_openai(prompt)
