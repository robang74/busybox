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

CLANG_ROOT = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/lib/clang"
CLANG_VERSION = sorted(CLANG_ROOT.iterdir())[-1].name
CLANG_RUNTIME = CLANG_ROOT / CLANG_VERSION / "lib/linux"

ANDROID_LIB = SYSROOT / f"usr/lib/aarch64-linux-android/{ANDROID_API}"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

print("NDK:", NDK_PATH)
print("Clang runtime:", CLANG_RUNTIME)

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
# Apply base config
# ------------------------------------------------

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

# ------------------------------------------------
# Create override config
# ------------------------------------------------

print("Creating override config")

override_file = Path("android_override.config")

override_file.write_text("""

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

CONFIG_LOADFONT=n
CONFIG_SETFONT=n
CONFIG_KBD_MODE=n
CONFIG_DUMPKMAP=n

CONFIG_HOSTID=n
CONFIG_MDEV=n

CONFIG_MOUNT=n
CONFIG_UMOUNT=n
CONFIG_PIVOT_ROOT=n

CONFIG_STATIC=y

""")

env = os.environ.copy()
env["KCONFIG_ALLCONFIG"] = str(override_file)

# ------------------------------------------------
# Resolve config (BusyBox requires oldconfig)
# ------------------------------------------------

print("Resolving BusyBox config")

run("yes '' | make oldconfig", env=env)

# ------------------------------------------------
# Compiler configuration
# ------------------------------------------------

CC = f"{TOOLCHAIN}/aarch64-linux-android{ANDROID_API}-clang"

env["CC"] = CC
env["LD"] = CC
env["HOSTCC"] = "gcc"
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
    f"HOSTCC={env['HOSTCC']}",
    f"AR={env['AR']}",
    f"RANLIB={env['RANLIB']}",
    f"STRIP={env['STRIP']}",
    f"CFLAGS={env['CFLAGS']}",
    f"LDFLAGS={env['LDFLAGS']}"
], env=env)

# ------------------------------------------------
# Package binary
# ------------------------------------------------

print("Packaging BusyBox")

run_list(["cp", "busybox", str(OUT_DIR / "busybox")])
run_list(["chmod", "+x", str(OUT_DIR / "busybox")])

print()
print("Build complete")
print("Binary location:", OUT_DIR / "busybox")
