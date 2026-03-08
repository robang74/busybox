#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

# ------------------------------------------------
# Configuration
# ------------------------------------------------

ANDROID_API = "21"

NDK_PATH = os.environ.get("NDK_PATH")
if not NDK_PATH:
    raise RuntimeError("NDK_PATH environment variable not set")

NDK_PATH = Path(NDK_PATH)

TOOLCHAIN = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/bin"
SYSROOT = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/sysroot"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------
# Detect clang runtime automatically
# ------------------------------------------------

CLANG_ROOT = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/lib/clang"
CLANG_VERSION = sorted(CLANG_ROOT.iterdir())[-1].name
CLANG_RUNTIME = CLANG_ROOT / CLANG_VERSION / "lib/linux"

ANDROID_LIB = SYSROOT / f"usr/lib/aarch64-linux-android/{ANDROID_API}"

print("NDK Path:", NDK_PATH)
print("Clang Runtime:", CLANG_RUNTIME)

# ------------------------------------------------
# Helpers
# ------------------------------------------------

def run(cmd, env=None):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def run_list(cmd, env=None):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

# ------------------------------------------------
# Clean previous build
# ------------------------------------------------

print("Cleaning previous build")
run_list(["make", "distclean"])

# ------------------------------------------------
# Apply Android config
# ------------------------------------------------

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

# ------------------------------------------------
# Override config
# ------------------------------------------------

print("Creating override config")

override_file = Path("android_override.config")

override_file.write_text("""

# Disable init
CONFIG_INIT=n
CONFIG_FEATURE_USE_INITTAB=n
CONFIG_FEATURE_INIT_SCTTY=n
CONFIG_FEATURE_INIT_SYSLOG=n
CONFIG_FEATURE_INIT_COREDUMPS=n
CONFIG_BOOTCHARTD=n

# Disable login utilities
CONFIG_LOGIN=n
CONFIG_GETTY=n
CONFIG_SU=n

# Disable runit
CONFIG_RUNSV=n
CONFIG_RUNSVDIR=n
CONFIG_SV=n
CONFIG_SVC=n
CONFIG_SVLOGD=n

# Disable kernel utilities
CONFIG_MDEV=n
CONFIG_MOUNT=n
CONFIG_UMOUNT=n
CONFIG_PIVOT_ROOT=n

# Disable console tools
CONFIG_LOADFONT=n
CONFIG_SETFONT=n
CONFIG_KBD_MODE=n
CONFIG_DUMPKMAP=n

# Disable host-only tools
CONFIG_HOSTID=n

# Static build
CONFIG_STATIC=y

""")

env = os.environ.copy()
env["KCONFIG_ALLCONFIG"] = str(override_file)

# ------------------------------------------------
# Resolve configuration (non-interactive)
# ------------------------------------------------

print("Resolving config")

run_list([
    "make",
    "olddefconfig"
], env=env)

# ------------------------------------------------
# Compiler setup
# ------------------------------------------------

CC = f"{TOOLCHAIN}/aarch64-linux-android{ANDROID_API}-clang"

env["CC"] = CC
env["LD"] = CC
env["AR"] = f"{TOOLCHAIN}/llvm-ar"
env["RANLIB"] = f"{TOOLCHAIN}/llvm-ranlib"
env["STRIP"] = f"{TOOLCHAIN}/llvm-strip"

env["CFLAGS"] = f"--sysroot={SYSROOT} -Os"
env["LDFLAGS"] = f"--sysroot={SYSROOT} -L{ANDROID_LIB} -L{CLANG_RUNTIME}"

# ------------------------------------------------
# Build BusyBox
# ------------------------------------------------

print("Building BusyBox")

run_list([
    "make",
    "-j4",
    "ARCH=arm64",
    f"CC={env['CC']}",
    f"LD={env['LD']}",
    f"AR
