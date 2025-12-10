import sqlite3
import os 
import logging

try:
    FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")
    if not FLET_APP_STORAGE_DATA:
        # fallback to a sane default inside the user's home directory
        FLET_APP_STORAGE_DATA = os.path.join(os.path.expanduser("~"), ".flet", "temp_storage")
    conn = sqlite3.connect(os.path.join(FLET_APP_STORAGE_DATA, "financeapp.db"), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    logging.info(f"Database connection created at {FLET_APP_STORAGE_DATA}")

except Exception as e:
    logging.error(f"Error creating database connection: {e}", exc_info=True)
