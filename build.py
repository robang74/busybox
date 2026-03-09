#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

ANDROID_API = "21"

NDK_PATH = os.environ["NDK_PATH"]
NDK = Path(NDK_PATH)

TOOLCHAIN = NDK / "toolchains/llvm/prebuilt/linux-x86_64"
BIN = TOOLCHAIN / "bin"
SYSROOT = TOOLCHAIN / "sysroot"

TARGET = f"aarch64-linux-android{ANDROID_API}"

CC = BIN / f"{TARGET}-clang"

OUT = Path("release")
OUT.mkdir(exist_ok=True)

def run(cmd, env=None):
    print(cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def run_list(cmd, env=None):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

print("Cleaning")
run_list(["make", "distclean"])

print("Loading config")
run_list(["cp", "busybox.config", ".config"])

env = os.environ.copy()

env["ARCH"] = "arm64"
env["CROSS_COMPILE"] = ""

env["CC"] = str(CC)
env["AR"] = str(BIN / "llvm-ar")
env["RANLIB"] = str(BIN / "llvm-ranlib")
env["STRIP"] = str(BIN / "llvm-strip")
env["HOSTCC"] = "gcc"

env["CFLAGS"] = f"--target={TARGET} --sysroot={SYSROOT} -Os"
env["LDFLAGS"] = f"--target={TARGET} --sysroot={SYSROOT}"

print("Resolving config")
run("yes '' | make oldconfig", env=env)

print("Building")
run_list(["make", "-j4"], env=env)

print("Packaging")

run_list(["cp", "busybox", str(OUT / "busybox")])
run_list(["chmod", "+x", str(OUT / "busybox")])

print("Done")
