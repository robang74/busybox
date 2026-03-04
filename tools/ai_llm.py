import os, requests
from ai_config import OPENAI_MODEL

def call_llm(prompt):

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
