from config import FLET_APP_STORAGE_DATA

import logging
import os

try:
    log_dir = os.path.join(FLET_APP_STORAGE_DATA, "applogs.log")
    logging.basicConfig(
        filename=log_dir,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Logger initialized.")
    logging.info(f"Log file located at: {log_dir}")

except Exception as e:
    logging.error(f"Error initializing logger: {e}", exc_info=True)