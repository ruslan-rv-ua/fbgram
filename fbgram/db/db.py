from pathlib import Path

from piccolo.engine.sqlite import SQLiteEngine

sqlite_path = Path(__file__).resolve().parent / "database.sqlite"
database = SQLiteEngine(path=str(sqlite_path))
