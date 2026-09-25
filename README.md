# Telegram Do'kon Boti — MVP

Python 3.11+ va `aiogram 3` asosida yozilgan. Ma'lumotlar bazasi — SQLite (`shop.db`, avtomatik yaratiladi).

## Nima qilinishi kerak — qadam-baqadam ishga tushirish

### 1. Python o'rnatilganini tekshiring
```
python3 --version
```
3.11 yoki undan yuqori bo'lishi kerak.

### 2. Loyihani papkaga tushiring va kutubxonalarni o'rnating
```
cd telegram_shop_bot
pip install -r requirements.txt
```
(Agar "externally-managed-environment" xatosi chiqsa: `pip install -r requirements.txt --break-system-packages`
yoki virtual environment yarating: `python3 -m venv venv && source venv/bin/activate`)

### 3. Bot tokenini oling
- Telegram'da **@BotFather** ga yozing
- `/newbot` buyrug'ini bering, nomini kiriting
- Sizga token beriladi (masalan `123456:ABC-DEF...`)

### 4. O'z Telegram User ID'ingizni oling
- Telegram'da **@userinfobot** ga yozing — u sizga ID raqamingizni (masalan `987654321`) beradi

### 5. Konfiguratsiya (.env fayli)
```
cp .env.example .env
```
So'ng `.env` faylini ochib, haqiqiy qiymatlarni kiriting:
```
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=987654321
```
`.env` fayli `.gitignore` ichida — u hech qachon GitHub'ga yuklanmaydi, token xavfsiz qoladi.

### 6. Botni ishga tushirish
```
python3 main.py
```
Terminal'da "Bot ishga tushdi" kabi loglar ko'rinsa — bot ishlamoqda. Telegram'da o'z botingizga `/start` yuboring.

### 7. O'zingizni admin sifatida sinab ko'rish
Admin panelni ochish uchun botga `/admin` buyrug'ini yuboring (faqat `ADMIN_IDS`da ko'rsatilgan ID uchun ishlaydi).

## GitHub bilan ishlash

### Repo'ga birinchi marta yuklash

```
cd telegram_shop_bot
git init
git add .
git commit -m "Initial commit: Telegram shop bot MVP"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/REPO_NOMI.git
git push -u origin main
```

⚠️ **Muhim:** `.env` fayli `.gitignore` ichida — u GitHub'ga hech qachon yuklanmaydi, token oshkor bo'lib qolmaydi. Faqat `.env.example` (bo'sh namuna) yuklanadi.

### Boshqa kompyuter/serverda klonlab ishga tushirish

```
git clone https://github.com/SIZNING_USERNAME/REPO_NOMI.git
cd REPO_NOMI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env faylini ochib, BOT_TOKEN va ADMIN_IDS'ni kiriting
python3 main.py
```

### Keyingi o'zgarishlarni yuklash

```
git add .
git commit -m "O'zgartirish tavsifi"
git push
```

### Deploy qilishda (VPS/server)

Serverda ham xuddi shunday: repo klonlanadi, `.env` **serverning o'zida** qo'lda yaratiladi (hech qachon git orqali yuborilmaydi), so'ng bot `systemd` yoki `screen`/`tmux`/`pm2` kabi vosita bilan doimiy ishlaydigan qilib ishga tushiriladi.

## Birinchi sozlash tartibi (admin sifatida)

1. `/admin` → **⚙️ Sozlamalar** → do'kon nomi, salomlashuv matni, manzil, ish vaqti, kontaktlarni kiriting
2. **➕ Mahsulot qo'shish** orqali birinchi kategoriya va mahsulotlarni qo'shing
3. Mijoz sifatida (boshqa Telegram akkaunt yoki shunchaki botga qayta `/start` bilan) to'liq jarayonni sinab ko'ring
4. Test buyurtma yarating, admin panelda uni ko'ring, statusini o'zgartiring, "To'landi" deb belgilang

## MVP doirasi — nima bor, nima yo'q

**Bor:**
- To'liq ikki tilli (RU/UZ) interfeys
- Katalog, savat, checkout, Toshkent/boshqa hudud yetkazib berish logikasi
- Lokatsiya yuborish imkoniyati
- To'lov: admin qo'lda "To'landi" deb belgilaydi (Click/Payme keyingi bosqichda qo'shiladi)
- To'liq admin panel: mahsulot CRUD, buyurtmalar, statuslar, sozlamalar, rassilka, statistika
- Admin bilan bog'lanish (support) oqimi

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
├── main.py              # bot ishga tushirish nuqtasi
├── config.py             # token, admin ID'lar
├── db/database.py        # barcha SQL/CRUD funksiyalar
├── utils/texts.py        # RU/UZ matnlar
├── utils/states.py       # FSM holatlari (bosqichma-bosqich dialoglar)
├── keyboards/            # tugmalar
└── handlers/              # bot mantig'i (client_*.py va admin_*.py)
```

## Muhim texnik eslatma

Bu — ishlaydigan, test qilingan MVP skeleti, lekin production'ga chiqarishdan oldin:
- `BOT_TOKEN`ni kodga emas, faqat environment variable orqali bering
- Katalog kattalashsa, `get_products_by_category` uchun pagination qo'shish tavsiya etiladi
- Rassilka (`admin_broadcast.py`) katta foydalanuvchi bazasida Telegram rate-limit'ga urilishi mumkin — hozirgi `BROADCAST_DELAY` sozlamasini kerak bo'lsa oshiring
