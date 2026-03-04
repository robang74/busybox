from ai_config import BUILD_CMD, PROJECT_ROOT
import subprocess, sys

def ensure_busybox_config():
    import pathlib
    if not (PROJECT_ROOT / ".config").exists():
        subprocess.run("make defconfig", cwd=PROJECT_ROOT, shell=True)

def run_build():

    ensure_busybox_config()

    with open("build.log", "wb") as f:

        p = subprocess.Popen(
            BUILD_CMD,
            cwd=PROJECT_ROOT,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        for line in p.stdout:
            sys.stdout.buffer.write(line)
            f.write(line)

    return p.wait()
