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

TOOLCHAIN = Path(NDK_PATH) / "toolchains/llvm/prebuilt/linux-x86_64/bin"
SYSROOT = Path(NDK_PATH) / "toolchains/llvm/prebuilt/linux-x86_64/sysroot"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------
# Helpers
# ------------------------------------------------

def run(cmd):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True)

def run_list(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

# ------------------------------------------------
# Clean previous builds
# ------------------------------------------------

print("Cleaning previous build")
run_list(["make", "distclean"])

# ------------------------------------------------
# Configure BusyBox
# ------------------------------------------------

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

# ------------------------------------------------
# Resolve config automatically
# ------------------------------------------------

print("Resolving BusyBox config")
run("yes '' | make oldconfig")

# ------------------------------------------------
# Force-disable Android incompatible features
# ------------------------------------------------

print("Applying Android config overrides")

config_file = Path(".config")

with open(config_file, "a") as f:
    f.write("""

# Android compatibility overrides

# Disable BusyBox init subsystem
# CONFIG_INIT is not set
# CONFIG_FEATURE_USE_INITTAB is not set
# CONFIG_FEATURE_INIT_SCTTY is not set
# CONFIG_FEATURE_INIT_SYSLOG is not set
# CONFIG_FEATURE_INIT_COREDUMPS is not set
# CONFIG_BOOTCHARTD is not set

# Disable power utilities
# CONFIG_HALT is not set
# CONFIG_REBOOT is not set
# CONFIG_POWEROFF is not set

# Disable login utilities
# CONFIG_LOGIN is not set
# CONFIG_GETTY is not set
# CONFIG_SU is not set

# Disable runit
# CONFIG_RUNSV is not set
# CONFIG_RUNSVDIR is not set
# CONFIG_SV is not set
# CONFIG_SVC is not set
# CONFIG_SVLOGD is not set

# Disable console tools
# CONFIG_LOADFONT is not set
# CONFIG_SETFONT is not set
# CONFIG_KBD_MODE is not set
# CONFIG_DUMPKMAP is not set

# Disable incompatible libc features
# CONFIG_HOSTID is not set

# Disable device manager
# CONFIG_MDEV is not set

# Disable mount utilities
# CONFIG_MOUNT is not set
# CONFIG_UMOUNT is not set
# CONFIG_PIVOT_ROOT is not set

# Static binary
CONFIG_STATIC=y

""")

# Reprocess config
run("yes '' | make oldconfig")

# ------------------------------------------------
# Build BusyBox
# ------------------------------------------------

print("Building BusyBox")

run_list([
    "make",
    "-j4",
    "ARCH=arm64",
    f"CC={TOOLCHAIN}/aarch64-linux-android{ANDROID_API}-clang",
    f"AR={TOOLCHAIN}/llvm-ar",
    f"RANLIB={TOOLCHAIN}/llvm-ranlib",
    f"STRIP={TOOLCHAIN}/llvm-strip",
    f"CFLAGS=--sysroot={SYSROOT} -Os",
    f"LDFLAGS=--sysroot={SYSROOT}",
])

# ------------------------------------------------
# Package binary
# ------------------------------------------------

print("Packaging BusyBox")

run_list(["cp", "busybox", str(OUT_DIR / "busybox")])
run_list(["chmod", "+x", str(OUT_DIR / "busybox")])

print()
print("Build complete")
print(f"Binary location: {OUT_DIR}/busybox")
