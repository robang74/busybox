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

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

TARGET = f"aarch64-linux-android{ANDROID_API}"

print("NDK:", NDK_PATH)
print("Target:", TARGET)

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
# Clean build
# ------------------------------------------------

print("Cleaning previous build")
run_list(["make", "distclean"])

# ------------------------------------------------
# Apply base config
# ------------------------------------------------

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

# ------------------------------------------------
# Override BusyBox configuration
# ------------------------------------------------

print("Creating Android override config")

override = Path("android_override.config")

override.write_text("""

# Disable BusyBox init subsystem
CONFIG_INIT=n
CONFIG_FEATURE_USE_INITTAB=n
CONFIG_FEATURE_INIT_SCTTY=n
CONFIG_FEATURE_INIT_SYSLOG=n
CONFIG_FEATURE_INIT_COREDUMPS=n
CONFIG_BOOTCHARTD=n

# Disable power utilities
CONFIG_HALT=n
CONFIG_REBOOT=n
CONFIG_POWEROFF=n

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

# Disable device manager
CONFIG_MDEV=n

# Disable incompatible libc feature
CONFIG_HOSTID=n

# Android requires dynamic linking
# CONFIG_STATIC is not set

""")

env = os.environ.copy()
env["KCONFIG_ALLCONFIG"] = str(override)

# ------------------------------------------------
# Resolve config automatically
# ------------------------------------------------

print("Resolving BusyBox config")

run("yes '' | make oldconfig", env=env)

# ------------------------------------------------
# Compiler configuration
# ------------------------------------------------

CC = TOOLCHAIN / f"{TARGET}-clang"

env["CC"] = str(CC)
env["LD"] = str(CC)
env["HOSTCC"] = "gcc"
env["AR"] = str(TOOLCHAIN / "llvm-ar")
env["RANLIB"] = str(TOOLCHAIN / "llvm-ranlib")
env["STRIP"] = str(TOOLCHAIN / "llvm-strip")

env["CFLAGS"] = f"--target={TARGET} -Os -fPIC"
env["LDFLAGS"] = f"--target={TARGET}"

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
