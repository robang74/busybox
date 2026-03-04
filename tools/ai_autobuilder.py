#!/usr/bin/env python3
import os, sys, subprocess, json, tempfile, re, pathlib

PROVIDER = os.getenv("PROVIDER", "openai")  # default to openai now
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_ATTEMPTS = int(os.getenv("AI_BUILDER_ATTEMPTS", "3"))
BUILD_CMD = os.getenv("BUILD_CMD", "make -j")
PROJECT_ROOT = pathlib.Path(os.getenv("PROJECT_ROOT", ".")).resolve()

PROMPT = """You are an automated build fixer. You are working in a Git repository.
Goal: Fix build/test failures by editing files.

Repository summary:
{repo_tree}

Recent changes (git diff HEAD~5..HEAD, if any):
{recent_diff}

Build command:
{build_cmd}

Build log (last 400 lines, most recent first):
{build_tail}

Key constraints:
- Return ONLY a valid unified diff starting with '---' and '+++' chunks.
- Do not include explanations outside of the diff.
- Keep edits minimal and safe.
- If config/tooling changes are needed (e.g., CMake/Gradle/PlatformIO), include those file changes in the diff.

Now propose a patch as unified diff to fix the error.
"""

def run(cmd, cwd=PROJECT_ROOT, capture=False, check=False):
    if capture:
        return subprocess.run(cmd, cwd=cwd, shell=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)
    else:
        return subprocess.run(cmd, cwd=cwd, shell=True, check=check)

def git(*args, capture=False):
    return run("git " + " ".join(args), capture=capture)

def get_repo_tree():
    out = run("git ls-files || true", capture=True)
    files = out.stdout.strip().splitlines()
    return "\n".join(files[:200])

def get_recent_diff():
    out = run("git log --oneline -n 1 || true", capture=True)
    if out.stdout.strip() == "":
        return "(no recent commits)"
    diff = run("git diff --unified=2 -M -C HEAD~5..HEAD || true", capture=True)
    return diff.stdout[-8000:]

def tail_build_log(lines=400):
    p = pathlib.Path("build.log")
    if not p.exists():
        return "(no build log)"
    data = p.read_text(errors="ignore").splitlines()
    return "\n".join(data[-lines:])

def run_build():
    with open("build.log", "wb") as f:
        p = subprocess.Popen(BUILD_CMD, cwd=PROJECT_ROOT, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout:
            sys.stdout.buffer.write(line)
            f.write(line)
    return p.wait()

def call_llm(prompt):
    import requests
    key = os.environ["OPENAI_API_KEY"]
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role":"user","content":prompt}],
        "temperature": 0.2
    }
    r = requests.post(url, headers={"Authorization": f"Bearer {key}",
                                    "Content-Type":"application/json"}, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def extract_unified_diff(text):
    m = re.search(r'(?ms)^--- [^\n]+\n\+\+\+ [^\n]+\n', text)
    if not m:
        return None
    start = m.start()
    return text[start:].strip()

def apply_patch(diff_text):
    tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch")
    tmp.write(diff_text)
    tmp.close()
    try:
        git("add", "-A")
        run("git diff --staged > .pre_ai_fix.patch || true")
        run(f"git apply --reject --whitespace=fix {tmp.name}", capture=True)
        git("add", "-A")
        run('git commit -m "ai-autobuilder: apply automatic fix" || true')
        return True
    except Exception as e:
        print("Patch apply failed:", e)
        return False
    finally:
        os.unlink(tmp.name)

def main():
    print("== AI Autobuilder ==")
    print("Project:", PROJECT_ROOT)
    if not (PROJECT_ROOT / ".git").exists():
        run("git init")
        run('git config user.name "ai-autobuilder"')
        run('git config user.email "ai-autobuilder@local"')
        git("add", "-A")
        run('git commit -m "ai-autobuilder: initial snapshot" || true')

    code = run_build()
    if code == 0:
        print("✅ Build already succeeds. Nothing to do.")
        return 0

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        print(f"\n== Attempt {attempts}/{MAX_ATTEMPTS} ==")
        prompt = PROMPT.format(
            repo_tree=get_repo_tree(),
            recent_diff=get_recent_diff(),
            build_cmd=BUILD_CMD,
            build_tail=tail_build_log()
        )
        llm_out = call_llm(prompt)
        diff = extract_unified_diff(llm_out)
        if not diff:
            print("LLM did not return a unified diff. Aborting this attempt.")
            break

        print("\n--- Proposed diff (truncated) ---\n")
        print(diff[:1500])
        print("\n--- end preview ---\n")

        if not apply_patch(diff):
            print("Could not apply patch. Stopping.")
            break

        code = run_build()
        if code == 0:
            print("✅ Build fixed!")
            return 0

    print("❌ Still failing after attempts.")
    print("Check build.log and .pre_ai_fix.patch to revert:  git apply -R .pre_ai_fix.patch")
    return 1

if __name__ == "__main__":
    sys.exit(main())
