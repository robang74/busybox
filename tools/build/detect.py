import pathlib

def detect_build_type(repo):

    repo = pathlib.Path(repo)

    if (repo / "Makefile").exists():
        if (repo / "applets").exists() or (repo / "busybox").exists():
            return "busybox"
        return "make"

    if (repo / "platformio.ini").exists():
        return "platformio"

    if (repo / "CMakeLists.txt").exists():
        return "cmake"

    if (repo / "build.gradle").exists():
        return "gradle"

    return "unknown"
