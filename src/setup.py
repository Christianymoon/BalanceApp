from config import FLET_APP_STORAGE_DATA

import logging
import os

try:

    if os.path.exists(FLET_APP_STORAGE_DATA) and FLET_APP_STORAGE_DATA:
        log_dir = os.path.join(FLET_APP_STORAGE_DATA, "applogs.log")
    else:
        log_dir = "./applogs.log"

except Exception as e:
    log_dir = "./applogs.log"

try:
    logging.basicConfig(
        filename=log_dir,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Logger initialized.")
    logging.info(f"Log file located at: {log_dir}")
    logging.info(f"FLET_APP_STORAGE_DATA STATUS: {FLET_APP_STORAGE_DATA}")

except Exception as e:
    logging.error(f"Error initializing logger: {e}", exc_info=True)
    logging.info("Logger initialized at ./applogs.log")