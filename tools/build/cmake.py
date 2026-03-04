class CMakeBuilder:

    name = "cmake"

    def detect(self, root):

        return (root / "CMakeLists.txt").exists()

    def build_command(self):

        return "cmake -B build && cmake --build build"

    def hint(self):

        return """
CMake project.

Common issues:
- missing libraries
- incorrect CMake flags
"""
