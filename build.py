#!/usr/bin/env python3
import os
import subprocess
import urllib.request
import tarfile
from pathlib import Path

# -------------------
# Configuration
# -------------------
BUSYBOX_VERSION = "1.36.1"
ANDROID_API = "21"
NDK_PATH = os.environ.get("NDK_PATH", "/path/to/android-ndk-r26d")
TOOLCHAIN = f"{NDK_PATH}/toolchains/llvm/prebuilt/linux-x86_64/bin"
SYSROOT = f"{TOOLCHAIN}/../sysroot"

OUT_DIR = Path("release")
OUT_DIR.mkdir(exist_ok=True)

# -------------------
# Download BusyBox
# -------------------
url = f"https://busybox.net/downloads/busybox-{BUSYBOX_VERSION}.tar.bz2"
tar_file = Path(f"busybox-{BUSYBOX_VERSION}.tar.bz2")
src_dir = Path(f"busybox-{BUSYBOX_VERSION}")

if not tar_file.exists():
    print(f"Downloading BusyBox {BUSYBOX_VERSION}...")
    urllib.request.urlretrieve(url, tar_file)

if not src_dir.exists():
    print(f"Extracting {tar_file}...")
    with tarfile.open(tar_file, "r:bz2") as tar:
        tar.extractall()

# -------------------
# Configure BusyBox
# -------------------
os.chdir(src_dir)

print("Running defconfig...")
subprocess.run(["make", "defconfig"], check=True)

# Apply Android-friendly tweaks
config_file = Path(".config")
with open(config_file, "r") as f:
    text = f.read()

# Disable init (Android incompatible)
text = text.replace("CONFIG_INIT=y", "# CONFIG_INIT is not set")
# Enable static build
text = text.replace("# CONFIG_STATIC is not set", "CONFIG_STATIC=y")

with open(config_file, "w") as f:
    f.write(text)

# -------------------
# Build BusyBox
# -------------------
print("Building BusyBox...")
subprocess.run([
    "make", "-j4",
    f"CC={TOOLCHAIN}/aarch64-linux-android{ANDROID_API}-clang",
    f"AR={TOOLCHAIN}/llvm-ar",
    f"RANLIB={TOOLCHAIN}/llvm-ranlib",
    f"STRIP={TOOLCHAIN}/llvm-strip",
    f"CFLAGS=--sysroot={SYSROOT} -Os",
    f"LDFLAGS=--sysroot={SYSROOT}"
], check=True)

# -------------------
# Package BusyBox
# -------------------
OUT_DIR.mkdir(exist_ok=True)
subprocess.run(["cp", "busybox", str(OUT_DIR / "busybox")], check=True)
subprocess.run(["chmod", "+x", str(OUT_DIR / "busybox")], check=True)

print(f"BusyBox ARM64 built successfully: {OUT_DIR / 'busybox'}")
