import pathlib

TEMPLATE = """
def build():
    print("Running {name} build logic")
"""

def generate(name):

    p = pathlib.Path(__file__).parent / f"{name}.py"

    if p.exists():
        return

    p.write_text(TEMPLATE.format(name=name))
