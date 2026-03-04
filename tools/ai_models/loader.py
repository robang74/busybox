import subprocess

def call_local_model(prompt, model="deepseek-coder"):
    p = subprocess.run(
        ["ollama", "run", model, "-p", prompt],
        capture_output=True,
        text=True
    )
    return p.stdout
