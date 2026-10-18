"""Import every UniLED platform against the installed Home Assistant (no hardware).
Run with the Python of an environment that has `homeassistant` installed, from the repo root."""
import importlib
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import homeassistant.const as c

print("Home Assistant", c.__version__)
failed = 0
for name in ("", ".config_flow", ".light", ".number", ".select", ".sensor", ".switch", ".button", ".scene", ".coordinator", ".entity"):
    mod = "custom_components.uniled" + name
    try:
        importlib.import_module(mod)
        print("ok  ", mod)
    except Exception:
        failed += 1
        print("FAIL", mod)
        print("    " + traceback.format_exc().strip().splitlines()[-1])
sys.exit(1 if failed else 0)
