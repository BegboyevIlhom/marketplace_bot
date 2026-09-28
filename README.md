# Telegram Do'kon Boti — MVP

Python 3.11+ va `aiogram 3` asosida yozilgan. Ma'lumotlar bazasi — **PostgreSQL** (Render'da bepul yaratiladigan turi).

## Nega SQLite emas, Postgres?

Render (va Railway kabi ko'plab bepul platformalar)ning bepul Web Service'lari **diskni saqlamaydi** — bot "uxlab" qolib qayta uyg'onganda, fayllar (shu jumladan SQLite bazasi) o'chib ketadi. Postgres esa **alohida, doimiy xizmat** — bot qayta ishga tushsa ham ma'lumotlar saqlanadi.

---

## Python versiyasi haqida muhim eslatma

Loyihada `.python-version` va `runtime.txt` fayllari bor — bular Render, Railway va boshqa ko'pgina platformalarga **aynan Python 3.11.9**dan foydalanishni buyuradi. Bu shart, chunki juda yangi Python versiyalarida (3.13, 3.14) `pydantic-core` kutubxonasi uchun tayyor paket (wheel) hali chiqmagan bo'lishi mumkin va build xatolik beradi. Agar platforma bu fayllarni o'qimasa, qo'lda `PYTHON_VERSION=3.11.9` environment variable qo'shing.

## Render'ga bepul joylashtirish — qadam-baqadam

### 1. Postgres bazangizni tayyorlang (agar hali yaratmagan bo'lsangiz)
Render dashboard → **New** → **PostgreSQL** → nom bering → **Create Database**.

### 2. Ulanish manzilini oling
Bazangiz sahifasida **"Connections"** bo'limiga tushing va **"External Database URL"** qatoridagi 👁 (ko'z) belgisini bosib, to'liq manzilni nusxalab oling. U taxminan shunday ko'rinadi:
```
postgresql://user:password@dpg-xxxxx.oregon-postgres.render.com/dbname
```

### 3. Web Service yarating
- Render dashboard → **New** → **Web Service**
- GitHub repo'ingizni tanlang (avtorizatsiya so'raladi, birinchi marta ulanish kerak)
- Quyidagilarni kiriting:
  - **Name:** ixtiyoriy (masalan `telegram-shop-bot`)
  - **Runtime:** Python 3
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `python3 main.py`
  - **Instance Type:** **Free**

### 4. Environment Variables (muhim!)
Web Service sozlamalarida **"Environment"** bo'limiga o'ting va qo'shing:

| Key | Value |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `ADMIN_IDS` | Sizning Telegram User ID'ingiz (raqam) |
| `DATABASE_URL` | 2-qadamda olgan "External Database URL" |

`PORT`ni qo'shmang — Render buni o'zi avtomatik beradi.

### 5. Deploy qiling
**"Create Web Service"** tugmasini bosing. Render avtomatik `requirements.txt`ni o'rnatadi va botni ishga tushiradi. Loglarni **"Logs"** bo'limida kuzatib borishingiz mumkin — `Health-check server ...-portda ishga tushdi` degan qator chiqsa, hammasi to'g'ri ishlayapti.

### 6. Botni "uxlab qolishdan" saqlash (UptimeRobot, bepul)

Render'ning bepul Web Service'i 15 daqiqa harakatsizlikdan keyin uxlab qoladi. Buni oldini olish uchun:

1. **uptimerobot.com**'da bepul ro'yxatdan o'ting
2. **"+ New Monitor"** → Monitor Type: **HTTP(s)**
3. URL sifatida Render bergan manzilingizni kiriting (masalan `https://telegram-shop-bot.onrender.com`)
4. Monitoring Interval: **5 daqiqa**
5. Saqlang

Shu bilan UptimeRobot har 5 daqiqada botingizga "salom" berib turadi, u hech qachon uxlab qolmaydi — va bu ham **butunlay bepul**.

---

## Lokal kompyuterda sinash (ixtiyoriy)

```bash
git clone https://github.com/SIZNING_USERNAME/REPO_NOMI.git
cd REPO_NOMI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env faylini ochib BOT_TOKEN, ADMIN_IDS, DATABASE_URL kiriting
python3 main.py
```

## Birinchi sozlash tartibi (admin sifatida)

1. Botga `/start` yuboring, til tanlang, telefon raqamingizni ulashing
2. `/admin` yuboring — admin panel ochiladi (faqat `ADMIN_IDS`dagi ID uchun)
3. **⚙️ Sozlamalar** → do'kon nomi, salomlashuv matni, manzil, ish vaqti, kontaktlarni kiriting
4. **➕ Mahsulot qo'shish** orqali birinchi kategoriya va mahsulotlarni qo'shing
5. Boshqa Telegram akkaunt bilan mijoz sifatida to'liq jarayonni sinab ko'ring

## MVP doirasi — nima bor, nima yo'q

**Bor:**
- To'liq ikki tilli (RU/UZ) interfeys
- Katalog, savat, checkout, Toshkent/boshqa hudud yetkazib berish logikasi
- Lokatsiya yuborish imkoniyati
- To'lov: admin qo'lda "To'landi" deb belgilaydi (Click/Payme keyingi bosqichda qo'shiladi)
- To'liq admin panel: mahsulot CRUD, buyurtmalar, statuslar, sozlamalar, rassilka, statistika
- Admin bilan bog'lanish (support) oqimi
- PostgreSQL — Render'ning bepul tarifida ham ma'lumotlar yo'qolmaydi

**Keyingi bosqichga qoldirilgan (MVP'da yo'q):**
- Click / Payme onlayn to'lov integratsiyasi
- O'z-o'zi olib ketish
- Fiskal chek
- Promo-kod / bonus tizimi
- Kuryer uchun alohida rol
- Hudud bo'yicha avtomatik narx hisoblash (geocoding)
- CSV/XLSX eksport

## Fayl tuzilishi

```
telegram_shop_bot/
├── main.py              # bot ishga tushirish nuqtasi + health-check server
├── config.py             # token, admin ID'lar, Postgres ulanish manzili
├── db/database.py        # barcha SQL/CRUD funksiyalar (PostgreSQL/asyncpg)
├── utils/texts.py        # RU/UZ matnlar
├── utils/states.py       # FSM holatlari (bosqichma-bosqich dialoglar)
├── keyboards/            # tugmalar
└── handlers/              # bot mantig'i (client_*.py va admin_*.py)
```

## Muhim eslatmalar

- Render'ning **bepul Postgres bazasi** cheklangan muddatga (odatda ~30 kun) beriladi, keyin uni saqlash uchun to'lovli rejaga o'tish yoki yangi bepul baza yaratish kerak bo'ladi — buni bazangiz sahifasidagi ogohlantirishdan kuzatib boring
- `BOT_TOKEN` va `DATABASE_URL`ni hech qachon kodga yozmang yoki GitHub'ga yuklamang — faqat Environment Variables orqali
- Katalog kattalashsa, `get_products_by_category` uchun pagination qo'shish tavsiya etiladi
- Rassilka (`admin_broadcast.py`) katta foydalanuvchi bazasida Telegram rate-limit'ga urilishi mumkin — hozirgi `BROADCAST_DELAY` sozlamasini kerak bo'lsa oshiring
