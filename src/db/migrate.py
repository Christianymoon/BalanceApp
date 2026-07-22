import sqlite3
from pathlib import Path
import logging

SCRIPT_DIR = Path(__file__).parent
MIGRATIONS_DIR = SCRIPT_DIR / "migrations"

def make_migrations(conn) -> None:
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY)""")
        cursor.execute("""SELECT COALESCE(MAX(version), 0) FROM schema_migrations """)
        current_version = cursor.fetchone()[0]
        migrations_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for migration in migrations_files:
            version = int(migration.stem.split("_")[0])
            if version > current_version:
                print(f"Ejecutando Migracion {version}")
                sql = migration.read_text(encoding="utf-8")
                cursor.executescript(sql)
                cursor.execute(
                    "INSERT INTO schema_migrations(version) VALUES(?)",
                    (version,)
                )
                conn.commit()
        cursor.close()
    except Exception as e:
        logging.error("Exception as triggered on make migrations", exc_info=True)



if __name__ == "__main__":
    make_migrations()
