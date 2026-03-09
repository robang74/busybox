#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

ANDROID_API = "21"

NDK_PATH = os.environ.get("NDK_PATH")
if not NDK_PATH:
    raise RuntimeError("NDK_PATH environment variable not set")

NDK_PATH = Path(NDK_PATH)

TOOLCHAIN = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64"
BIN = TOOLCHAIN / "bin"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

TARGET = f"aarch64-linux-android{ANDROID_API}"

print("NDK:", NDK_PATH)
print("Target:", TARGET)

def run(cmd, env=None):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def run_list(cmd, env=None):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

# ------------------------------------------------
# Clean
# ------------------------------------------------

print("Cleaning previous build")
run_list(["make", "distclean"])

# ------------------------------------------------
# Base config
# ------------------------------------------------

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

# ------------------------------------------------
# Override config
# ------------------------------------------------

override = Path("android_override.config")

override.write_text("""

CONFIG_INIT=n
CONFIG_FEATURE_USE_INITTAB=n
CONFIG_FEATURE_INIT_SCTTY=n
CONFIG_FEATURE_INIT_SYSLOG=n
CONFIG_FEATURE_INIT_COREDUMPS=n
CONFIG_BOOTCHARTD=n

CONFIG_HALT=n
CONFIG_REBOOT=n
CONFIG_POWEROFF=n

CONFIG_LOGIN=n
CONFIG_GETTY=n
CONFIG_SU=n

CONFIG_RUNSV=n
CONFIG_RUNSVDIR=n
CONFIG_SV=n
CONFIG_SVC=n
CONFIG_SVLOGD=n

CONFIG_MDEV=n
CONFIG_HOSTID=n

# Android must use dynamic linking
# CONFIG_STATIC is not set

""")

env = os.environ.copy()
env["KCONFIG_ALLCONFIG"] = str(override)

# ------------------------------------------------
# Resolve config
# ------------------------------------------------

print("Resolving BusyBox config")
run("yes '' | make oldconfig", env=env)

# ------------------------------------------------
# Toolchain setup
# ------------------------------------------------

env["ARCH"] = "arm64"
env["CROSS_COMPILE"] = str(BIN / "aarch64-linux-android-")

env["CC"] = str(BIN / f"{TARGET}-clang")
env["LD"] = env["CC"]
env["AR"] = str(BIN / "llvm-ar")
env["RANLIB"] = str(BIN / "llvm-ranlib")
env["STRIP"] = str(BIN / "llvm-strip")
env["HOSTCC"] = "gcc"

env["CFLAGS"] = "-Os"
env["LDFLAGS"] = ""

# ------------------------------------------------
# Build
# ------------------------------------------------

print("Building BusyBox")

run_list([
    "make",
    "-j4"
], env=env)

# ------------------------------------------------
# Package
# ------------------------------------------------

print("Packaging BusyBox")

run_list(["cp", "busybox", str(OUT_DIR / "busybox")])
run_list(["chmod", "+x", str(OUT_DIR / "busybox")])

print()
print("Build complete")
print("Binary:", OUT_DIR / "busybox")
