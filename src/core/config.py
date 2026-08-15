import os

DEFAULT_PROFILE_PIC = "./assets/avatar/profile.png"
PROFILE_PIC_KEY = "christianymoon.finance.profile_pic"

try:
    FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")  # ANDROID MODE
    ASSETS_DIR = "assets"
except Exception:
    FLET_APP_STORAGE_DATA = "/"
