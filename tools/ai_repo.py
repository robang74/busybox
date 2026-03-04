from ai_config import PROJECT_ROOT
import subprocess, pathlib

def run(cmd, capture=False):
    if capture:
        return subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True,
                              text=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    else:
        return subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True)

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
