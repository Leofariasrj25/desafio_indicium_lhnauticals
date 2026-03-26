from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(PROJECT_ROOT) / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ANALYTICS_DATA_DIR = DATA_DIR / "analytics"

if not DATA_DIR.exists() or not RAW_DATA_DIR.exists():
    raise FileNotFoundError("Cannot find data dir (data/)")

if not PROCESSED_DATA_DIR.exists():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

if not ANALYTICS_DATA_DIR.exists():
    ANALYTICS_DATA_DIR.mkdir(parents=True, exist_ok=True)
