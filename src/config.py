import os 

try: 
    FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA") # ANDROID MODE
except Exception:
    FLET_APP_STORAGE_DATA = "/"