from pathlib import Path

API_DIR = Path(__file__).resolve().parent.parent
DB_PATH = API_DIR / "data" / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
SEED = 20240917
