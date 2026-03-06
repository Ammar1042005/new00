import os
import json

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DEFAULTS = {
    "tesseract_path": "",
    "libreoffice_path": "",
    "ghostscript_path": ""
}

def load() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            out = DEFAULTS.copy()
            out.update({k: str(v) for k, v in (data or {}).items() if k in DEFAULTS})
            return out
    except Exception:
        return DEFAULTS.copy()

def save(partial: dict) -> dict:
    cfg = load()
    for k, v in (partial or {}).items():
        if k in DEFAULTS:
            cfg[k] = str(v or "")
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg
