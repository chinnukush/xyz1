import re
from os import environ

# -------------------------
# Helper
# -------------------------
def str_to_bool(val, default=False):
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")

# =========================================================
# 🤖 BOT BASIC INFORMATION
# =========================================================
API_ID = int(environ.get("API_ID", "15671595"))
API_HASH = environ.get("API_HASH", "bb8f36f9c39a24c7f8b2acbc7ea8c60a")
BOT_TOKEN = environ.get("BOT_TOKEN", "8542548465:AAGDJzASZI1PU_kb8oF5GUpwaO5r9Ot8j5c")
PORT = int(environ.get("PORT", "8080"))
TIMEZONE = environ.get("TIMEZONE", "Asia/Kolkata")
OWNER_USERNAME = environ.get("OWNER_USERNAME", "helperxsupport")

# =========================================================
# 💾 DATABASE CONFIGURATION
# =========================================================
DB_URL = environ.get("DATABASE_URI", "mongodb+srv://anikush8310_db_user:89zE00vwQMcxo0Xd@cluster0.td3ydlm.mongodb.net/?appName=Cluster0")
DB_NAME = environ.get("DATABASE_NAME", "testing")

# =========================================================
# 📢 CHANNELS & ADMINS
# =========================================================
ADMINS = int(environ.get("ADMINS", "7253187871"))

LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002220189899"))
PREMIUM_LOGS = int(environ.get("PREMIUM_LOGS", "-1002220189899"))
VERIFIED_LOG = int(environ.get("VERIFIED_LOG", "-1002220189899"))

POST_CHANNEL = int(environ.get("POST_CHANNEL", "-1002275153880"))
VIDEO_CHANNEL = int(environ.get("VIDEO_CHANNEL", "-1002723763926"))
BRAZZER_CHANNEL = int(environ.get("BRAZZER_CHANNEL", "-1002275153880"))

# Auth channels list
auth_channel_str = environ.get("AUTH_CHANNEL", "-1002275153880")
AUTH_CHANNEL = [int(x) for x in auth_channel_str.split() if x.strip().lstrip("-").isdigit()]

# =========================================================
# ⚙️ FEATURES & TOGGLES  (FIXED)
# =========================================================
FSUB = str_to_bool(environ.get("FSUB"), True)
IS_VERIFY = str_to_bool(environ.get("IS_VERIFY"), False)
POST_SHORTLINK = str_to_bool(environ.get("POST_SHORTLINK"), True)
SEND_POST = str_to_bool(environ.get("SEND_POST"), True)
PROTECT_CONTENT = str_to_bool(environ.get("PROTECT_CONTENT"), True)

# =========================================================
# 🔢 LIMITS
# =========================================================
DAILY_LIMIT = int(environ.get("DAILY_LIMIT", "2"))
VERIFICATION_DAILY_LIMIT = int(environ.get("VERIFICATION_DAILY_LIMIT", "20"))
PREMIUM_DAILY_LIMIT = int(environ.get("PREMIUM_DAILY_LIMIT", "50"))

# =========================================================
# 🔗 SHORTLINK & VERIFICATION
# =========================================================
SHORTLINK_URL = environ.get("SHORTLINK_URL", "arolinks.com")
SHORTLINK_API = environ.get("SHORTLINK_API", "45b6928d65d1c1dfc2d52d052d879b9b02dd7fe3")
POST_SHORTLINK_URL = environ.get("POST_SHORTLINK_URL", "arolinks.com")
POST_SHORTLINK_API = environ.get("POST_SHORTLINK_API", "45b6928d65d1c1dfc2d52d052d879b9b02dd7fe3")
VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "180"))
TUTORIAL_LINK = environ.get("TUTORIAL_LINK", "https://t.me/Brand_moviess/6")

# =========================================================
# 💳 PAYMENT SETTINGS
# =========================================================
UPI_ID = environ.get("UPI_ID", "kushalhari@slc")
QR_CODE_IMAGE = environ.get("QR_CODE_IMAGE", "https://i.ibb.co/21ZPjBNw/071d44198b51.jpg")

# =========================================================
# 🖼️ IMAGES
# =========================================================
START_PIC = environ.get("START_PIC", "https://i.ibb.co/v6j5cmNx/571f351e38dc.jpg")
AUTH_PICS = environ.get("AUTH_PICS", "https://i.ibb.co/RkFKXdzZ/ab3f2ad85d1b.jpg")
VERIFY_IMG = environ.get("VERIFY_IMG", "https://image.zaw-myo.workers.dev/image/e3031533-e96c-4e57-b248-a8f3726d4211")
NO_IMG = environ.get("NO_IMG", "")

# =========================================================
# 🌐 WEB APP
# =========================================================
WEB_APP_URL = environ.get("WEB_APP_URL", "")
