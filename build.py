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

CLANG_ROOT = NDK_PATH / "toolchains/llvm/prebuilt/linux-x86_64/lib/clang"
CLANG_VERSION = sorted(CLANG_ROOT.iterdir())[-1].name
CLANG_RUNTIME = CLANG_ROOT / CLANG_VERSION / "lib/linux"

ANDROID_LIB = SYSROOT / f"usr/lib/aarch64-linux-android/{ANDROID_API}"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

print("Using Clang runtime:", CLANG_RUNTIME)

def run(cmd, env=None):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def run_list(cmd, env=None):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

print("Cleaning previous build")
run_list(["make", "distclean"])

print("Applying android_ndk_defconfig")
run_list(["make", "android_ndk_defconfig"])

print("Creating Android override config")

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

env["ARCH"] = "arm64"

env["CROSS_COMPILE"] = str(TOOLCHAIN) + "/aarch64-linux-android-"

env["CC"] = f"{TOOLCHAIN}/aarch64-linux-android{ANDROID_API}-clang"
env["AR"] = f"{TOOLCHAIN}/llvm-ar"
env["RANLIB"] = f"{TOOLCHAIN}/llvm-ranlib"
env["STRIP"] = f"{TOOLCHAIN}/llvm-strip"

env["CFLAGS"] = f"--sysroot={SYSROOT} -Os"

env["LDFLAGS"] = (
    f"--sysroot={SYSROOT} "
    f"-L{ANDROID_LIB} "
    f"-L{CLANG_RUNTIME}"
)

print("Resolving BusyBox config with forced overrides")
run("yes '' | make oldconfig", env=env)

print("Building BusyBox")

run_list([
    "make",
    "-j4"
], env=env)

print("Packaging BusyBox")

run_list(["cp", "busybox", str(OUT_DIR / "busybox")])
run_list(["chmod", "+x", str(OUT_DIR / "busybox")])

print()
print("Build complete")
print(f"Binary location: {OUT_DIR}/busybox")
