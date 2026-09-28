import os
from dotenv import load_dotenv

# .env faylidan o'qiydi (agar fayl bo'lmasa, environment variable'lardan o'qishda davom etadi)
load_dotenv()

# BotFather'dan olingan token - .env faylida BOT_TOKEN=... shaklida beriladi
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin sifatida ruxsat berilgan Telegram User ID (raqam). Bir nechta bo'lsa vergul bilan ajrating.
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# PostgreSQL ulanish manzili - Render/Railway'dagi Postgres xizmatining
# "External Database URL" (lokal ishga tushirishda) yoki "Internal Database URL"
# (Render'ning o'zida, Web Service sifatida ishga tushirilganda) qiymati
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Render bepul Web Service HTTP portni talab qiladi (aks holda "sog'lom emas" deb hisoblaydi)
PORT = int(os.getenv("PORT", "8080"))

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
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL topilmadi. Render'dagi Postgres bazangizning "
        "'External Database URL' qiymatini .env fayliga DATABASE_URL=... shaklida kiriting."
    )


