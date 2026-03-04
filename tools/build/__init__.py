import pathlib

from .busybox import BusyBoxBuilder
from .xz import XZBuilder
from .radare2 import Radare2Builder
from .platformio import PlatformIOBuilder
from .cmake import CMakeBuilder
from .make import MakeBuilder


BUILDERS = [
    BusyBoxBuilder(),
    XZBuilder(),
    Radare2Builder(),
    PlatformIOBuilder(),
    CMakeBuilder(),
    MakeBuilder()
]


def detect_builder(project_root):

    for builder in BUILDERS:
        if builder.detect(project_root):
            return builder

    return MakeBuilder()
