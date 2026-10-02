"""
Barcha ma'lumotlar bazasi bilan ishlash funksiyalari shu yerda.
PostgreSQL (asyncpg) ishlatiladi - Render/Railway kabi platformalarda
bepul Web Service'lar diskni saqlamaydi (har restart'da fayllar o'chadi),
shuning uchun SQLite emas, alohida Postgres xizmati ishlatiladi.

Barcha funksiya nomlari va parametrlari handlers/*.py fayllarida ishlatilgan
holicha saqlangan - faqat ichki implementatsiya o'zgargan.
"""
import json
import time
import asyncpg

from config import DATABASE_URL

DEFAULT_SETTINGS = {
    "shop_name": "Do'kon",
    "greeting_ru": "Добро пожаловать! 👋\nЗдесь вы можете выбрать товары и оформить заказ.",
    "greeting_uz": "Xush kelibsiz! 👋\nBu yerda siz tovarlarni tanlab, buyurtma bera olasiz.",
    "about_ru": "Информация о компании пока не заполнена.",
    "about_uz": "Kompaniya haqida ma'lumot hali kiritilmagan.",
    "address": "-",
    "work_hours": "-",
    "contacts": "-",
    "delivery_price_tashkent": "30000",
    "free_delivery_threshold": "0",
    "payment_info": "To'lov kuryerga naqd yoki karta orqali amalga oshiriladi.",
    "cart_reminder_delay_hours": "2",
}

SETTINGS_LABELS = {
    "shop_name": {"ru": "Название магазина", "uz": "Do'kon nomi"},
    "greeting_ru": {"ru": "Приветствие (RU)", "uz": "Salomlashuv matni (RU)"},
    "greeting_uz": {"ru": "Приветствие (UZ)", "uz": "Salomlashuv matni (UZ)"},
    "about_ru": {"ru": "О компании (RU)", "uz": "Kompaniya haqida (RU)"},
    "about_uz": {"ru": "О компании (UZ)", "uz": "Kompaniya haqida (UZ)"},
    "address": {"ru": "Адрес", "uz": "Manzil"},
    "work_hours": {"ru": "График работы", "uz": "Ish vaqti"},
    "contacts": {"ru": "Контакты", "uz": "Kontaktlar"},
    "delivery_price_tashkent": {"ru": "Стоимость доставки (Ташкент)", "uz": "Yetkazib berish narxi (Toshkent)"},
    "free_delivery_threshold": {"ru": "Бесплатная доставка от суммы (0 = выкл)", "uz": "Shu summadan bepul yetkazish (0 = o'chirilgan)"},
    "payment_info": {"ru": "Текст об оплате", "uz": "To'lov haqida matn"},
    "cart_reminder_delay_hours": {
        "ru": "Напоминание о корзине через (часов)",
        "uz": "Savat eslatmasi necha soatdan keyin",
    },
}

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT UNIQUE NOT NULL,
                language TEXT,
                phone TEXT,
                name TEXT,
                created_at BIGINT
            );

            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name_ru TEXT NOT NULL,
                name_uz TEXT NOT NULL,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                category_id INTEGER NOT NULL,
                name_ru TEXT, name_uz TEXT,
                short_ru TEXT, short_uz TEXT,
                full_ru TEXT, full_uz TEXT,
                price INTEGER,
                old_price INTEGER,
                photo_main TEXT,
                photos_extra TEXT DEFAULT '[]',
                characteristics_ru TEXT DEFAULT '',
                characteristics_uz TEXT DEFAULT '',
                available INTEGER DEFAULT 1,
                is_hidden INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'unpaid',
                city TEXT,
                delivery_price INTEGER,
                address TEXT,
                location_lat DOUBLE PRECISION,
                location_lon DOUBLE PRECISION,
                comment TEXT,
                recipient_name TEXT,
                recipient_phone TEXT,
                items_total INTEGER,
                total INTEGER,
                created_at BIGINT
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER,
                name_ru TEXT, name_uz TEXT,
                price INTEGER,
                quantity INTEGER
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS support_messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                text TEXT,
                created_at BIGINT,
                answered INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS cart_reminders (
                user_id INTEGER PRIMARY KEY,
                last_cart_change_at BIGINT,
                reminder_sent INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, product_id)
            );

            CREATE TABLE IF NOT EXISTS promo_codes (
                code TEXT PRIMARY KEY,
                discount_type TEXT NOT NULL,
                discount_value INTEGER NOT NULL,
                active INTEGER DEFAULT 1,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                created_at BIGINT
            );

            CREATE TABLE IF NOT EXISTS staff (
                tg_id BIGINT PRIMARY KEY,
                role TEXT NOT NULL,
                name TEXT,
                added_at BIGINT
            );

            CREATE TABLE IF NOT EXISTS admin_pins (
                tg_id BIGINT PRIMARY KEY,
                pin TEXT NOT NULL
            );
            """
        )
        # Eski (allaqachon ishlab turgan) bazalarga yangi ustunlarni xavfsiz qo'shish.
        # CREATE TABLE IF NOT EXISTS mavjud jadvalga yangi ustun qo'sha olmaydi,
        # shuning uchun buni alohida qilamiz - mavjud Railway/Supabase bazalari
        # qo'lda o'chirilmasdan avtomatik yangilanadi.
        await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS promo_code TEXT")
        await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS discount_amount INTEGER DEFAULT 0")
        await conn.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS completed_by BIGINT")
        await conn.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS added_by BIGINT")

        for k, v in DEFAULT_SETTINGS.items():
            await conn.execute(
                "INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO NOTHING",
                k, v,
            )


def _d(record) -> dict | None:
    return dict(record) if record else None


# ---------- USERS ----------

async def get_or_create_user(tg_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE tg_id=$1", tg_id)
        if row:
            return _d(row)
        await conn.execute(
            "INSERT INTO users (tg_id, created_at) VALUES ($1, $2)", tg_id, int(time.time())
        )
        row = await conn.fetchrow("SELECT * FROM users WHERE tg_id=$1", tg_id)
        return _d(row)


async def set_user_language(tg_id: int, lang: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET language=$1 WHERE tg_id=$2", lang, tg_id)


async def set_user_contact(tg_id: int, phone: str, name: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET phone=$1, name=$2 WHERE tg_id=$3", phone, name, tg_id
        )


async def get_user(tg_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE tg_id=$1", tg_id)
        return _d(row)


async def get_user_by_internal_id(internal_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id=$1", internal_id)
        return _d(row)


async def get_all_user_tg_ids() -> list[int]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT tg_id FROM users WHERE tg_id IS NOT NULL")
        return [r["tg_id"] for r in rows]


async def get_all_users() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY id")
        return [_d(r) for r in rows]


# ---------- CATEGORIES ----------

async def add_category(name_ru: str, name_uz: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "INSERT INTO categories (name_ru, name_uz) VALUES ($1, $2) RETURNING id",
            name_ru, name_uz,
        )


async def get_categories() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM categories WHERE is_deleted=0 ORDER BY id")
        return [_d(r) for r in rows]


async def get_category(cat_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM categories WHERE id=$1", cat_id)
        return _d(row)


# ---------- PRODUCTS ----------

async def add_product(data: dict) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """INSERT INTO products
            (category_id, name_ru, name_uz, short_ru, short_uz, full_ru, full_uz,
             price, old_price, photo_main, photos_extra, characteristics_ru,
             characteristics_uz, available, added_by)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
            RETURNING id""",
            data["category_id"], data["name_ru"], data["name_uz"],
            data.get("short_ru", data.get("full_ru", "")), data.get("short_uz", data.get("full_uz", "")),
            data["full_ru"], data["full_uz"],
            data["price"], data.get("old_price"), data["photo_main"],
            json.dumps(data.get("photos_extra", [])),
            data.get("characteristics_ru", ""), data.get("characteristics_uz", ""),
            1 if data.get("available", True) else 0,
            data.get("added_by"),
        )


async def get_products_by_category(cat_id: int, include_hidden: bool = False, sort: str = "default") -> list[dict]:
    order_clause = "ORDER BY id"
    if sort == "price_asc":
        order_clause = "ORDER BY price ASC"
    elif sort == "price_desc":
        order_clause = "ORDER BY price DESC"
    pool = await get_pool()
    async with pool.acquire() as conn:
        if include_hidden:
            rows = await conn.fetch(
                f"SELECT * FROM products WHERE category_id=$1 AND is_deleted=0 {order_clause}", cat_id
            )
        else:
            rows = await conn.fetch(
                f"SELECT * FROM products WHERE category_id=$1 AND is_deleted=0 AND is_hidden=0 {order_clause}",
                cat_id,
            )
        return [_d(r) for r in rows]


async def search_products(query: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        like = f"%{query}%"
        rows = await conn.fetch(
            """SELECT * FROM products
               WHERE is_deleted=0 AND is_hidden=0 AND available=1
               AND (name_ru ILIKE $1 OR name_uz ILIKE $1)
               ORDER BY id LIMIT 30""",
            like,
        )
        return [_d(r) for r in rows]


async def get_product(product_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM products WHERE id=$1", product_id)
        return _d(row)


async def update_product_field(product_id: int, field: str, value):
    allowed = {
        "name_ru", "name_uz", "short_ru", "short_uz", "full_ru", "full_uz",
        "price", "old_price", "photo_main", "characteristics_ru",
        "characteristics_uz", "available", "category_id",
    }
    if field not in allowed:
        raise ValueError(f"Bunday maydonni o'zgartirib bo'lmaydi: {field}")
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE products SET {field}=$1 WHERE id=$2", value, product_id)


async def set_product_hidden(product_id: int, hidden: bool):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE products SET is_hidden=$1 WHERE id=$2", 1 if hidden else 0, product_id
        )


async def delete_product(product_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE products SET is_deleted=1 WHERE id=$1", product_id)


# ---------- CART ----------

async def _touch_cart_reminder(conn, user_id: int):
    """Savat o'zgarganda - eslatma 'soatini' yangidan boshlaydi."""
    await conn.execute(
        "INSERT INTO cart_reminders (user_id, last_cart_change_at, reminder_sent) VALUES ($1,$2,0) "
        "ON CONFLICT (user_id) DO UPDATE SET last_cart_change_at=excluded.last_cart_change_at, reminder_sent=0",
        user_id, int(time.time()),
    )


async def _clear_cart_reminder(conn, user_id: int):
    await conn.execute("DELETE FROM cart_reminders WHERE user_id=$1", user_id)


async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, quantity FROM cart_items WHERE user_id=$1 AND product_id=$2",
            user_id, product_id,
        )
        if row:
            await conn.execute(
                "UPDATE cart_items SET quantity=$1 WHERE id=$2", row["quantity"] + qty, row["id"]
            )
        else:
            await conn.execute(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES ($1,$2,$3)",
                user_id, product_id, qty,
            )
        await _touch_cart_reminder(conn, user_id)


async def get_cart(user_id: int) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT ci.id as cart_item_id, ci.quantity, p.*
               FROM cart_items ci JOIN products p ON p.id = ci.product_id
               WHERE ci.user_id=$1""",
            user_id,
        )
        return [_d(r) for r in rows]


async def update_cart_qty(cart_item_id: int, delta: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT quantity, user_id FROM cart_items WHERE id=$1", cart_item_id)
        if not row:
            return 0
        user_id = row["user_id"]
        new_qty = max(0, row["quantity"] + delta)
        if new_qty == 0:
            await conn.execute("DELETE FROM cart_items WHERE id=$1", cart_item_id)
        else:
            await conn.execute("UPDATE cart_items SET quantity=$1 WHERE id=$2", new_qty, cart_item_id)
        remaining = await conn.fetchval("SELECT COUNT(*) FROM cart_items WHERE user_id=$1", user_id)
        if remaining == 0:
            await _clear_cart_reminder(conn, user_id)
        else:
            await _touch_cart_reminder(conn, user_id)
        return new_qty


async def remove_cart_item(cart_item_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT user_id FROM cart_items WHERE id=$1", cart_item_id)
        await conn.execute("DELETE FROM cart_items WHERE id=$1", cart_item_id)
        if row:
            remaining = await conn.fetchval(
                "SELECT COUNT(*) FROM cart_items WHERE user_id=$1", row["user_id"]
            )
            if remaining == 0:
                await _clear_cart_reminder(conn, row["user_id"])


async def clear_cart(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM cart_items WHERE user_id=$1", user_id)
        await _clear_cart_reminder(conn, user_id)


async def get_users_needing_reminder(threshold_ts: int) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT u.* FROM cart_reminders cr
               JOIN users u ON u.id = cr.user_id
               WHERE cr.last_cart_change_at <= $1 AND cr.reminder_sent = 0""",
            threshold_ts,
        )
        return [_d(r) for r in rows]


async def mark_reminder_sent(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE cart_reminders SET reminder_sent=1 WHERE user_id=$1", user_id)


# ---------- ORDERS ----------

async def create_order(user_id: int, cart: list[dict], city: str, delivery_price,
                        address: str, lat, lon, comment: str,
                        recipient_name: str, recipient_phone: str,
                        promo_code: str | None = None, discount_amount: int = 0) -> dict:
    items_total = sum(item["price"] * item["quantity"] for item in cart)
    total = items_total - discount_amount + (delivery_price or 0)
    status = "pending"
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            order_id = await conn.fetchval(
                """INSERT INTO orders
                (user_id, status, payment_status, city, delivery_price, address,
                 location_lat, location_lon, comment, recipient_name, recipient_phone,
                 items_total, total, created_at, promo_code, discount_amount)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
                RETURNING id""",
                user_id, status, "unpaid", city, delivery_price, address, lat, lon,
                comment, recipient_name, recipient_phone, items_total, total,
                int(time.time()), promo_code, discount_amount,
            )
            for item in cart:
                await conn.execute(
                    """INSERT INTO order_items (order_id, product_id, name_ru, name_uz, price, quantity)
                       VALUES ($1,$2,$3,$4,$5,$6)""",
                    order_id, item["id"], item["name_ru"], item["name_uz"], item["price"], item["quantity"],
                )
    return {"id": order_id, "items_total": items_total, "total": total, "status": status}


async def get_order(order_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM orders WHERE id=$1", order_id)
        return _d(row)


async def get_order_items(order_id: int) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM order_items WHERE order_id=$1", order_id)
        return [_d(r) for r in rows]


async def get_user_orders(user_id: int, active: bool) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if active:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE user_id=$1 AND status NOT IN ('completed','cancelled') ORDER BY id DESC",
                user_id,
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE user_id=$1 AND status IN ('completed','cancelled') ORDER BY id DESC",
                user_id,
            )
        return [_d(r) for r in rows]


async def get_active_orders() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM orders WHERE status NOT IN ('completed','cancelled') ORDER BY id DESC"
        )
        return [_d(r) for r in rows]


async def get_history_orders(limit: int = 50) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM orders WHERE status IN ('completed','cancelled') ORDER BY id DESC LIMIT $1",
            limit,
        )
        return [_d(r) for r in rows]


async def search_orders(query: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        like = f"%{query}%"
        rows = await conn.fetch(
            """SELECT * FROM orders
               WHERE CAST(id AS TEXT)=$1 OR recipient_phone LIKE $2 OR recipient_name LIKE $2
               ORDER BY id DESC""",
            query, like,
        )
        return [_d(r) for r in rows]


async def update_order_status(order_id: int, status: str, handled_by: int | None = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        if status == "completed" and handled_by is not None:
            await conn.execute(
                "UPDATE orders SET status=$1, completed_by=$2 WHERE id=$3", status, handled_by, order_id
            )
        else:
            await conn.execute("UPDATE orders SET status=$1 WHERE id=$2", status, order_id)


async def set_delivery_price(order_id: int, price: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT items_total FROM orders WHERE id=$1", order_id)
        items_total = row["items_total"] if row else 0
        new_total = items_total + price
        await conn.execute(
            "UPDATE orders SET delivery_price=$1, total=$2, status='confirmed' WHERE id=$3",
            price, new_total, order_id,
        )
        return new_total


async def mark_order_paid(order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE orders SET payment_status='paid' WHERE id=$1", order_id)


# ---------- SETTINGS ----------

async def get_setting(key: str) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        value = await conn.fetchval("SELECT value FROM settings WHERE key=$1", key)
        return value or ""


async def set_setting(key: str, value: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES ($1, $2) "
            "ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value",
            key, value,
        )


async def get_all_settings() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT key, value FROM settings")
        return {r["key"]: r["value"] for r in rows}


# ---------- SUPPORT ----------

async def add_support_message(user_id: int, text: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "INSERT INTO support_messages (user_id, text, created_at) VALUES ($1,$2,$3) RETURNING id",
            user_id, text, int(time.time()),
        )


# ---------- STATS ----------

async def get_sales_stats(since_ts: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as revenue
               FROM orders WHERE payment_status='paid' AND created_at>=$1""",
            since_ts,
        )
        paid_count, revenue = row["cnt"], row["revenue"]

        total_orders = await conn.fetchval(
            "SELECT COUNT(*) FROM orders WHERE created_at>=$1", since_ts
        )

        top_rows = await conn.fetch(
            """SELECT oi.product_id, oi.name_ru, SUM(oi.quantity) as qty, SUM(oi.price*oi.quantity) as revenue
               FROM order_items oi JOIN orders o ON o.id = oi.order_id
               WHERE o.payment_status='paid' AND o.created_at>=$1
               GROUP BY oi.product_id, oi.name_ru ORDER BY qty DESC LIMIT 5""",
            since_ts,
        )
        top_products = [_d(r) for r in top_rows]

        avg_check = int(revenue / paid_count) if paid_count else 0

        return {
            "total_orders": total_orders,
            "paid_orders": paid_count,
            "revenue": revenue,
            "avg_check": avg_check,
            "top_products": top_products,
        }


# ---------- FAVORITES ----------

async def add_favorite(user_id: int, product_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO favorites (user_id, product_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
            user_id, product_id,
        )


async def remove_favorite(user_id: int, product_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM favorites WHERE user_id=$1 AND product_id=$2", user_id, product_id)


async def is_favorite(user_id: int, product_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        val = await conn.fetchval(
            "SELECT 1 FROM favorites WHERE user_id=$1 AND product_id=$2", user_id, product_id
        )
        return bool(val)


async def get_favorites(user_id: int) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT p.* FROM favorites f JOIN products p ON p.id = f.product_id
               WHERE f.user_id=$1 AND p.is_deleted=0 ORDER BY p.id""",
            user_id,
        )
        return [_d(r) for r in rows]


# ---------- PROMO CODES ----------

async def create_promo_code(code: str, discount_type: str, discount_value: int, max_uses: int | None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO promo_codes (code, discount_type, discount_value, max_uses, active, created_at)
               VALUES ($1,$2,$3,$4,1,$5)
               ON CONFLICT (code) DO UPDATE SET discount_type=excluded.discount_type,
               discount_value=excluded.discount_value, max_uses=excluded.max_uses, active=1""",
            code.upper(), discount_type, discount_value, max_uses, int(time.time()),
        )


async def get_promo_code(code: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM promo_codes WHERE code=$1", code.upper())
        return _d(row)


async def get_all_promo_codes() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM promo_codes ORDER BY created_at DESC")
        return [_d(r) for r in rows]


async def toggle_promo_code(code: str, active: bool):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE promo_codes SET active=$1 WHERE code=$2", 1 if active else 0, code.upper())


async def increment_promo_usage(code: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE code=$1", code.upper())


# ---------- STAFF (sotuvchi / kuryer rollari) ----------

async def add_staff(tg_id: int, role: str, name: str = ""):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO staff (tg_id, role, name, added_at) VALUES ($1,$2,$3,$4) "
            "ON CONFLICT (tg_id) DO UPDATE SET role=excluded.role, name=excluded.name",
            tg_id, role, name, int(time.time()),
        )


async def remove_staff(tg_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM staff WHERE tg_id=$1", tg_id)


async def get_staff_role(tg_id: int) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT role FROM staff WHERE tg_id=$1", tg_id)


async def get_all_staff() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM staff ORDER BY added_at")
        return [_d(r) for r in rows]


# ---------- ADMIN PIN ----------

async def set_admin_pin(tg_id: int, pin: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO admin_pins (tg_id, pin) VALUES ($1,$2) "
            "ON CONFLICT (tg_id) DO UPDATE SET pin=excluded.pin",
            tg_id, pin,
        )


async def get_admin_pin(tg_id: int) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT pin FROM admin_pins WHERE tg_id=$1", tg_id)


# ---------- XODIM STATISTIKASI ----------

async def get_staff_stats(tg_id: int) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        products_added = await conn.fetchval(
            "SELECT COUNT(*) FROM products WHERE added_by=$1", tg_id
        )
        orders_completed = await conn.fetchval(
            "SELECT COUNT(*) FROM orders WHERE completed_by=$1", tg_id
        )
        return {"products_added": products_added or 0, "orders_completed": orders_completed or 0}


# ---------- KATEGORIYA BO'YICHA TO'LIQ RO'YXAT (admin uchun, yashirin/mavjud bo'lmaganlar ham) ----------

async def get_all_products_in_category(cat_id: int) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM products WHERE category_id=$1 AND is_deleted=0 ORDER BY id", cat_id
        )
        return [_d(r) for r in rows]


async def count_products_per_category() -> dict:
    """Har bir kategoriyada nechta (o'chirilmagan) mahsulot borligini qaytaradi: {category_id: count}."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT category_id, COUNT(*) as cnt FROM products WHERE is_deleted=0 GROUP BY category_id"
        )
        return {r["category_id"]: r["cnt"] for r in rows}
