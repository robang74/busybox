#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

ANDROID_API = "21"

NDK_PATH = os.environ.get("NDK_PATH")
if not NDK_PATH:
    raise RuntimeError("NDK_PATH environment variable not set")

NDK_PATH = Path(NDK_PATH)

TOOLCHAIN = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/bin"
SYSROOT = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/sysroot"

# Android runtime libraries
ANDROID_LIB = SYSROOT / f"usr/lib/aarch64-linux-android/{ANDROID_API}"
CLANG_LIB = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/lib/clang/17/lib/linux"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

TARGET = f"aarch64-linux-android{ANDROID_API}"

print("NDK:", NDK_PATH)
print("Target:", TARGET)
print("Sysroot:", SYSROOT)

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
# BusyBox override config
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

# Android requires dynamic linking
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
# Compiler setup
# ------------------------------------------------

CC = TOOLCHAIN / f"{TARGET}-clang"

env["CC"] = str(CC)
env["LD"] = str(CC)
env["HOSTCC"] = "gcc"
env["AR"] = str(TOOLCHAIN / "llvm-ar")
env["RANLIB"] = str(TOOLCHAIN / "llvm-ranlib")
env["STRIP"] = str(TOOLCHAIN / "llvm-strip")

env["CFLAGS"] = (
    f"--target={TARGET} "
    f"--sysroot={SYSROOT} "
    "-Os -fPIC"
)

env["LDFLAGS"] = (
    f"--target={TARGET} "
    f"--sysroot={SYSROOT} "
    f"-L{ANDROID_LIB} "
    f"-L{CLANG_LIB}"
)

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
    f"HOSTCC={env['HOSTCC']}",
    f"AR={env['AR']}",
    f"RANLIB={env['RANLIB']}",
    f"STRIP={env['STRIP']}",
    f"CFLAGS={env['CFLAGS']}",
    f"LDFLAGS={env['LDFLAGS']}"
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
