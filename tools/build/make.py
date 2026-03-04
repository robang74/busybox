class MakeBuilder:

    name = "make"

    def detect(self, root):

        return (root / "Makefile").exists()

    def build_command(self):

        return "make -j"

    def hint(self):

        return """
Generic Make project.

Common issues:
- missing compiler flags
- missing headers
"""
