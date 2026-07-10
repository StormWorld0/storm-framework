import importlib.util
from pathlib import Path
import pytest

# Path to your modules folder
MODULES_DIR = "modules"


@pytest.mark.core
def get_all_modules():
    """
    He will search for .py files from the surface to the deepest.
    """
    modules = []
    base_path = Path("modules")
    if base_path.exists():
        for path in base_path.rglob("*.py"):
            if path.is_file() and path.name != "__init__.py":
                modules.append(str(path))

    return modules


@pytest.mark.security
@pytest.mark.parametrize("module_file", get_all_modules())
def test_module_load(module_file):
    """
    This test will try to load each module.
    If there is a contributor whose code has typos/errors, this test will be RED.
    """
    module_path = module_file
    module_name = Path(module_file).stem

    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            pytest.fail(f"Module {module_file} ERROR: Could not load spec")

        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        assert True
    except Exception as e:
        pytest.fail(f"Module {module_file} ERROR: {e}")
