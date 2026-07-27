from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    passed = 0
    for path in sorted(ROOT.glob("test_*.py")):
        module = _load_module(path)
        for name in dir(module):
            if name.startswith("test_") and callable(getattr(module, name)):
                getattr(module, name)()
                passed += 1
    print(f"{passed} tests passed")


if __name__ == "__main__":
    main()
