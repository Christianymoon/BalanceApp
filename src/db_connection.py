import sqlite3
import os 
import logging

try:
    FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA") # ANDROID MODE
    conn = sqlite3.connect(os.path.join(FLET_APP_STORAGE_DATA, "financeapp.db"), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")

except Exception as e:
    FLET_APP_STORAGE_DATA = "/"
    conn = sqlite3.connect("financeapp.db", check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    logging.error(f"Error accessing FLET_APP_STORAGE_DATA: {e}", exc_info=True)

