from pathlib import Path
import inspect

MODULE_ROOT = Path(inspect.getframeinfo(inspect.currentframe()).filename).parent
TRUE_ROOT = MODULE_ROOT.parent


def module_path(filename):
    return str(MODULE_ROOT.joinpath(filename).relative_to(TRUE_ROOT))
