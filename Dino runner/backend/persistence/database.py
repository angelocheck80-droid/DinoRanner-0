from contextlib import contextmanager
from pathlib import Path
import sqlite3


SCHEMA_VERSION = 1


class Database:
    def __init__(self, path=None):
        project_root = Path(__file__).resolve().parents[2]
        self.path = Path(path) if path else project_root / "data" / "game.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self):
        with self.connection() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version > SCHEMA_VERSION:
                raise RuntimeError(
                    f"Database schema version {version} is newer than supported version {SCHEMA_VERSION}"
                )
            if version == 0:
                schema_path = Path(__file__).with_name("schema.sql")
                connection.executescript(schema_path.read_text(encoding="utf-8"))
                connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
