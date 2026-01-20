import sqlite3
import os 
import logging
from config import FLET_APP_STORAGE_DATA

try:
    conn = sqlite3.connect(os.path.join(FLET_APP_STORAGE_DATA, "financeapp.db"), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    logging.info(f"Database connection created at {FLET_APP_STORAGE_DATA}")
except Exception as e:
    conn = sqlite3.connect(os.path.join("./", "financeapp.db"), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    logging.info(f"Database connection created at {os.path.join("./", "financeapp.db")}")