import os
from dotenv import load_dotenv

# .env faylidan o'qiydi (agar fayl bo'lmasa, environment variable'lardan o'qishda davom etadi)
load_dotenv()

# BotFather'dan olingan token - .env faylida BOT_TOKEN=... shaklida beriladi
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin sifatida ruxsat berilgan Telegram User ID (raqam). Bir nechta bo'lsa vergul bilan ajrating.
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

DB_PATH = os.getenv("DB_PATH", "shop.db")

# Rassilka (broadcast) paytida ketma-ket xabar yuborish orasidagi tanaffus (soniya)
# Telegram limitlariga urilib qolmaslik uchun
BROADCAST_DELAY = 0.05

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. .env faylini yarating (.env.example'dan nusxa oling) "
        "va BOT_TOKEN=... qiymatini kiriting."
    )
if not ADMIN_IDS:
    raise RuntimeError(
        "ADMIN_IDS topilmadi. .env faylida ADMIN_IDS=... (Telegram User ID) kiriting."
    )

