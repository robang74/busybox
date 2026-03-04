import tempfile, os, re, subprocess
from ai_config import PROJECT_ROOT

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

        subprocess.run("git add -A", cwd=PROJECT_ROOT, shell=True)

        subprocess.run(
            "git diff --staged > .pre_ai_fix.patch || true",
            cwd=PROJECT_ROOT,
            shell=True
        )

        subprocess.run(
            f"git apply --reject --whitespace=fix {tmp.name}",
            cwd=PROJECT_ROOT,
            shell=True
        )

        subprocess.run("git add -A", cwd=PROJECT_ROOT, shell=True)

        subprocess.run(
            'git commit -m "ai-autobuilder: apply automatic fix" || true',
            cwd=PROJECT_ROOT,
            shell=True
        )

        return True

    except Exception as e:
        print("Patch apply failed:", e)
        return False

    finally:
        os.unlink(tmp.name)
