from pathlib import Path

TRUE_ROOT = Path(__file__).parent.parent


def module_path(filename):
    return str(Path(__file__).parent.joinpath(filename).relative_to(TRUE_ROOT))
