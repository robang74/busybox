import os, pathlib

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
"""
