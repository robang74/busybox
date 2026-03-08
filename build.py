#!/usr/bin/env python3

import os
import subprocess
import urllib.request
import tarfile
from pathlib import Path

# ------------------------------------------------
# Configuration
# ------------------------------------------------

BUSYBOX_VERSION = "1.36.1"
ANDROID_API = "21"

NDK_PATH = os.environ.get("NDK_PATH", "")
if not NDK_PATH:
    raise RuntimeError("NDK_PATH environment variable not set")

TOOLCHAIN = f"{NDK_PATH}/toolchains/llvm/prebuilt/linux-x86_64/bin"
SYSROOT = f"{NDK_PATH}/toolchains/llvm/prebuilt/linux-x86_64/sysroot"

SRC_DIR = Path(f"busybox-{BUSYBOX_VERSION}")
TAR_FILE = Path(f"busybox-{BUSYBOX_VERSION}.tar.bz2")
OUT_DIR = Path("release")

OUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------
# Helper
# ------------------------------------------------

def run(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


# ------------------------------------------------
# Download BusyBox
# ------------------------------------------------

if not TAR_FILE.exists():
    print(f"Downloading BusyBox {BUSYBOX_VERSION}")
    urllib.request.urlretrieve(
        f"https://busybox.net/downloads/{TAR_FILE}",
        TAR_FILE
    )

if not SRC_DIR.exists():
    print("Extracting BusyBox")
    with tarfile.open(TAR_FILE, "r:bz2") as tar:
        tar.extractall()


# ------------------------------------------------
# Configure BusyBox
# ------------------------------------------------

os.chdir(SRC_DIR)

print("Using Android config")

run(["make", "android_ndk_defconfig"])

config_file = Path(".config")

cfg = config_file.read_text()

# Disable Linux console features
disable = [
    "CONFIG_LOADFONT",
    "CONFIG_SETFONT",
    "CONFIG_KBD_MODE",
    "CONFIG_DUMPKMAP",
]

for opt in disable:
    cfg = cfg.replace(f"{opt}=y", f"# {opt} is not set")

# Disable hostid
cfg = cfg.replace("CONFIG_HOSTID=y", "# CONFIG_HOSTID is not set")

# Disable init (Android doesn't use BusyBox init)
cfg = cfg.replace("CONFIG_INIT=y", "# CONFIG_INIT is not set")

# Enable static binary
cfg = cfg.replace("# CONFIG_STATIC is not set", "CONFIG_STATIC=y")

config_file.write_text(cfg)

# Regenerate headers
run(["make", "oldconfig"])


# ------------------------------------------------
# Build BusyBox
# ------------------------------------------------

print("Building BusyBox")

run([
    "make",
    "-j4",
    "ARCH=arm64",
    f"CC={TOOLCHAIN}/aarch64-linux-android{ANDROID_API}-clang",
    f"AR={TOOLCHAIN}/llvm-ar",
    f"RANLIB={TOOLCHAIN}/llvm-ranlib",
    f"STRIP={TOOLCHAIN}/llvm-strip",
    f"CFLAGS=--sysroot={SYSROOT} -Os",
    f"LDFLAGS=--sysroot={SYSROOT}"
])


# ------------------------------------------------
# Package
# ------------------------------------------------

print("Packaging")

OUT_DIR.mkdir(exist_ok=True)

run(["cp", "busybox", str(OUT_DIR / "busybox")])
run(["chmod", "+x", str(OUT_DIR / "busybox")])

print()
print("Build complete")
print(f"Binary location: {OUT_DIR}/busybox")
