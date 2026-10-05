#!/usr/bin/env python3
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "src" / "aruba_sign_cli" / "__init__.py"
PACKAGE_DIR = MODULE_PATH.parent

spec = importlib.util.spec_from_file_location(
    "aruba_sign_cli",
    MODULE_PATH,
    submodule_search_locations=[str(PACKAGE_DIR)],
)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load module from {MODULE_PATH}")

module = importlib.util.module_from_spec(spec)
sys.modules["aruba_sign_cli"] = module
spec.loader.exec_module(module)


if __name__ == "__main__":
    module.main()