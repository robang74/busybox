from ai_config import BUILD_CMD, PROJECT_ROOT
from build.detect import detect_build_type
from build.knowledge import record

import subprocess
import sys
import pathlib


def ensure_busybox_config():
    """
    Ensure BusyBox .config exists and is valid.
    """

    config = PROJECT_ROOT / ".config"

    if not config.exists():

        print("BusyBox: generating default config")

        subprocess.run(
            "make defconfig",
            cwd=PROJECT_ROOT,
            shell=True
        )

    else:

        # Ensure config matches source
        subprocess.run(
            "make oldconfig",
            cwd=PROJECT_ROOT,
            shell=True
        )


def run_build():

    build_type = detect_build_type(PROJECT_ROOT)

    print(f"Detected build type: {build_type}")

    if build_type == "busybox":
        ensure_busybox_config()

    log_file = pathlib.Path("build.log")

    with log_file.open("wb") as f:

        p = subprocess.Popen(
            BUILD_CMD,
            cwd=PROJECT_ROOT,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        if p.stdout is None:
            raise RuntimeError("Failed to capture build output")

        for line in p.stdout:

            sys.stdout.buffer.write(line)
            f.write(line)

    exit_code = p.wait()

    # read build log for history
    try:
        log_data = log_file.read_text(errors="ignore")
    except Exception:
        log_data = ""

    # record build attempt
    record(build_type, exit_code == 0, log_data)

    return {
        "exit_code": exit_code,
        "build_type": build_type
    }
