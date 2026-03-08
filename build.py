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

def run(cmd, env=None):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def run_list(cmd, env=None):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

# ------------------------------------------------
# Clean previous builds
# ------------------------------------------------

print("Cleaning previous build")
run_list(["make", "distclean"])

# ------------------------------------------------
# Apply Android base config
# ------------------------------------------------

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

# ------------------------------------------------
# Create forced config overrides
# ------------------------------------------------

print("Creating Android override config")

override_file = Path("android_override.config")

override_file.write_text("""

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

# Disable console utilities
CONFIG_LOADFONT=n
CONFIG_SETFONT=n
CONFIG_KBD_MODE=n
CONFIG_DUMPKMAP=n

# Disable incompatible libc features
CONFIG_HOSTID=n

# Disable device manager
CONFIG_MDEV=n

# Disable mount utilities
CONFIG_MOUNT=n
CONFIG_UMOUNT=n
CONFIG_PIVOT_ROOT=n

# Static binary
CONFIG_STATIC=y
""")

env = os.environ.copy()
env["KCONFIG_ALLCONFIG"] = str(override_file)

# ------------------------------------------------
# Re-resolve config with overrides
# ------------------------------------------------

print("Resolving BusyBox config with forced overrides")
run("yes '' | make oldconfig", env=env)

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
], env=env)

# ------------------------------------------------
# Package binary
# ------------------------------------------------

print("Packaging BusyBox")

run_list(["cp", "busybox", str(OUT_DIR / "busybox")])
run_list(["chmod", "+x", str(OUT_DIR / "busybox")])

print()
print("Build complete")
print(f"Binary location: {OUT_DIR}/busybox")
