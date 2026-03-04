#!/usr/bin/env python3
import os, sys, subprocess, json, tempfile, re, pathlib

PROVIDER = os.getenv("PROVIDER", "openai")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

MAX_ATTEMPTS = int(os.getenv("AI_BUILDER_ATTEMPTS", "3"))
BUILD_CMD = os.getenv("BUILD_CMD", "make -j")

PROJECT_ROOT = pathlib.Path(os.getenv("PROJECT_ROOT", ".")).resolve()

BUSYBOX_HINT = """
Project type: BusyBox

BusyBox build system rules:
- Uses Makefile + .config
- Configuration options defined in .config
- Build command usually: make
- Cross compile uses CC or CROSS_COMPILE
- Static builds require CONFIG_STATIC=y
- Regenerate config with: make oldconfig

Typical fixes:
- Enable CONFIG_STATIC=y
- Adjust CROSS_COMPILE
- Modify Makefile flags
- Fix missing headers
"""

PROMPT = """You are an automated build fixer working in a Git repository.

Goal:
Fix BusyBox build failures by editing files.

Repository files:
{repo_tree}

Recent git diff:
{recent_diff}

Build command:
{build_cmd}

Build log:
{build_tail}

Project notes:
{project_hint}

Rules:
- Return ONLY a unified diff
- Start with --- and +++
- Minimal safe edits
- Prefer fixing .config or Makefile for BusyBox

Generate patch now.
"""

def run(cmd, cwd=PROJECT_ROOT, capture=False, check=False):
    if capture:
        return subprocess.run(cmd, cwd=cwd, shell=True, text=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              check=check)
    else:
        return subprocess.run(cmd, cwd=cwd, shell=True, check=check)

def git(*args, capture=False):
    return run("git " + " ".join(args), capture=capture)

def get_repo_tree():
    out = run("git ls-files || true", capture=True)
    files = out.stdout.splitlines()
    return "\n".join(files[:200])

def get_recent_diff():
    diff = run("git diff --unified=2 -M -C HEAD~5..HEAD || true", capture=True)
    return diff.stdout[-8000:]

def tail_build_log(lines=400):
    p = pathlib.Path("build.log")
    if not p.exists():
        return "(no build log)"
    data = p.read_text(errors="ignore").splitlines()
    return "\n".join(data[-lines:])

def ensure_busybox_config():
    """Auto-create BusyBox config if missing"""
    if not (PROJECT_ROOT / ".config").exists():
        print("Generating BusyBox default config")
        run("make defconfig")

def run_build():
    ensure_busybox_config()

    with open("build.log", "wb") as f:
        p = subprocess.Popen(BUILD_CMD, cwd=PROJECT_ROOT, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        for line in p.stdout:
            sys.stdout.buffer.write(line)
            f.write(line)

    return p.wait()

def call_llm(prompt):
    import requests
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

def extract_unified_diff(text):
    m = re.search(r'(?ms)^--- [^\n]+\n\+\+\+ [^\n]+\n', text)
    if not m:
        return None
    return text[m.start():].strip()

def apply_patch(diff_text):
    tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch")
    tmp.write(diff_text)
    tmp.close()

    try:
        git("add -A")
        run("git diff --staged > .pre_ai_fix.patch || true")

        run(f"git apply --reject --whitespace=fix {tmp.name}", capture=True)

        git("add -A")
        run('git commit -m "ai-autobuilder: apply automatic fix" || true')

        return True

    except Exception as e:
        print("Patch apply failed:", e)
        return False

    finally:
        os.unlink(tmp.name)

def main():
    print("== AI BusyBox Autobuilder ==")

    if not (PROJECT_ROOT / ".git").exists():
        run("git init")
        run('git config user.name "ai-autobuilder"')
        run('git config user.email "ai@local"')
        git("add -A")
        run('git commit -m "initial snapshot" || true')

    code = run_build()

    if code == 0:
        print("Build already works.")
        return 0

    attempts = 0

    while attempts < MAX_ATTEMPTS:
        attempts += 1

        print(f"\nAttempt {attempts}/{MAX_ATTEMPTS}")

        prompt = PROMPT.format(
            repo_tree=get_repo_tree(),
            recent_diff=get_recent_diff(),
            build_cmd=BUILD_CMD,
            build_tail=tail_build_log(),
            project_hint=BUSYBOX_HINT
        )

        llm_out = call_llm(prompt)
        diff = extract_unified_diff(llm_out)

        if not diff:
            print("No valid patch returned.")
            break

        print("\nPatch preview:\n")
        print(diff[:1500])

        if not apply_patch(diff):
            break

        code = run_build()

        if code == 0:
            print("Build fixed!")
            return 0

    print("Still failing.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
