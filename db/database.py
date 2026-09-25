"""
Barcha ma'lumotlar bazasi bilan ishlash funksiyalari shu yerda.
SQLite (aiosqlite) ishlatilgan - MVP uchun yetarli, kerak bo'lsa keyin
PostgreSQL'ga ko'chirish uchun funksiya nomlarini o'zgartirmasdan
faqat shu faylni almashtirish kifoya.
"""
import json
import time
import aiosqlite

from config import DB_PATH

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
    "free_delivery_threshold": "0",  # 0 = bepul chegara yo'q
    "payment_info": "To'lov kuryerga naqd yoki karta orqali amalga oshiriladi.",
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
}


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                language TEXT,
                phone TEXT,
                name TEXT,
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_ru TEXT NOT NULL,
                name_uz TEXT NOT NULL,
                is_deleted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'unpaid',
                city TEXT,
                delivery_price INTEGER,
                address TEXT,
                location_lat REAL,
                location_lon REAL,
                comment TEXT,
                recipient_name TEXT,
                recipient_phone TEXT,
                items_total INTEGER,
                total INTEGER,
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT,
                created_at INTEGER,
                answered INTEGER DEFAULT 0
            );
            """
        )
        for k, v in DEFAULT_SETTINGS.items():
            await db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v)
            )
        await db.commit()


# ---------- USERS ----------

async def get_or_create_user(tg_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
        row = await cur.fetchone()
        if row:
            return dict(row)
        await db.execute(
            "INSERT INTO users (tg_id, created_at) VALUES (?, ?)", (tg_id, int(time.time()))
        )
        await db.commit()
        cur = await db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
        row = await cur.fetchone()
        return dict(row)


async def set_user_language(tg_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language=? WHERE tg_id=?", (lang, tg_id))
        await db.commit()


async def set_user_contact(tg_id: int, phone: str, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET phone=?, name=? WHERE tg_id=?", (phone, name, tg_id)
        )
        await db.commit()


async def get_user(tg_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_user_by_internal_id(internal_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE id=?", (internal_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_all_user_tg_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT tg_id FROM users WHERE tg_id IS NOT NULL")
        rows = await cur.fetchall()
        return [r[0] for r in rows]


# ---------- CATEGORIES ----------

async def add_category(name_ru: str, name_uz: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO categories (name_ru, name_uz) VALUES (?, ?)", (name_ru, name_uz)
        )
        await db.commit()
        return cur.lastrowid


async def get_categories() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM categories WHERE is_deleted=0 ORDER BY id")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_category(cat_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM categories WHERE id=?", (cat_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


# ---------- PRODUCTS ----------

async def add_product(data: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO products
            (category_id, name_ru, name_uz, short_ru, short_uz, full_ru, full_uz,
             price, old_price, photo_main, photos_extra, characteristics_ru,
             characteristics_uz, available)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                data["category_id"], data["name_ru"], data["name_uz"],
                data["short_ru"], data["short_uz"], data["full_ru"], data["full_uz"],
                data["price"], data.get("old_price"), data["photo_main"],
                json.dumps(data.get("photos_extra", [])),
                data.get("characteristics_ru", ""), data.get("characteristics_uz", ""),
                1 if data.get("available", True) else 0,
            ),
        )
        await db.commit()
        return cur.lastrowid


async def get_products_by_category(cat_id: int, include_hidden: bool = False) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        q = "SELECT * FROM products WHERE category_id=? AND is_deleted=0"
        if not include_hidden:
            q += " AND is_hidden=0"
        q += " ORDER BY id"
        cur = await db.execute(q, (cat_id,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_product(product_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM products WHERE id=?", (product_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def update_product_field(product_id: int, field: str, value):
    allowed = {
        "name_ru", "name_uz", "short_ru", "short_uz", "full_ru", "full_uz",
        "price", "old_price", "photo_main", "characteristics_ru",
        "characteristics_uz", "available", "category_id",
    }
    if field not in allowed:
        raise ValueError(f"Bunday maydonni o'zgartirib bo'lmaydi: {field}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE products SET {field}=? WHERE id=?", (value, product_id))
        await db.commit()


async def set_product_hidden(product_id: int, hidden: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE products SET is_hidden=? WHERE id=?", (1 if hidden else 0, product_id)
        )
        await db.commit()


async def delete_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET is_deleted=1 WHERE id=?", (product_id,))
        await db.commit()


# ---------- CART ----------

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, quantity FROM cart_items WHERE user_id=? AND product_id=?",
            (user_id, product_id),
        )
        row = await cur.fetchone()
        if row:
            await db.execute(
                "UPDATE cart_items SET quantity=? WHERE id=?", (row[1] + qty, row[0])
            )
        else:
            await db.execute(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?,?,?)",
                (user_id, product_id, qty),
            )
        await db.commit()


async def get_cart(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT ci.id as cart_item_id, ci.quantity, p.*
               FROM cart_items ci JOIN products p ON p.id = ci.product_id
               WHERE ci.user_id=?""",
            (user_id,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def update_cart_qty(cart_item_id: int, delta: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT quantity FROM cart_items WHERE id=?", (cart_item_id,))
        row = await cur.fetchone()
        if not row:
            return 0
        new_qty = max(0, row[0] + delta)
        if new_qty == 0:
            await db.execute("DELETE FROM cart_items WHERE id=?", (cart_item_id,))
        else:
            await db.execute(
                "UPDATE cart_items SET quantity=? WHERE id=?", (new_qty, cart_item_id)
            )
        await db.commit()
        return new_qty


async def remove_cart_item(cart_item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart_items WHERE id=?", (cart_item_id,))
        await db.commit()


async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
        await db.commit()


# ---------- ORDERS ----------

async def create_order(user_id: int, cart: list[dict], city: str, delivery_price,
                        address: str, lat, lon, comment: str,
                        recipient_name: str, recipient_phone: str) -> dict:
    items_total = sum(item["price"] * item["quantity"] for item in cart)
    total = items_total + (delivery_price or 0)
    status = "pending"
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO orders
            (user_id, status, payment_status, city, delivery_price, address,
             location_lat, location_lon, comment, recipient_name, recipient_phone,
             items_total, total, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id, status, "unpaid", city, delivery_price, address, lat, lon,
                comment, recipient_name, recipient_phone, items_total, total,
                int(time.time()),
            ),
        )
        order_id = cur.lastrowid
        for item in cart:
            await db.execute(
                """INSERT INTO order_items (order_id, product_id, name_ru, name_uz, price, quantity)
                   VALUES (?,?,?,?,?,?)""",
                (order_id, item["id"], item["name_ru"], item["name_uz"], item["price"], item["quantity"]),
            )
        await db.commit()
    return {"id": order_id, "items_total": items_total, "total": total, "status": status}


async def get_order(order_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_order_items(order_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_user_orders(user_id: int, active: bool) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if active:
            q = "SELECT * FROM orders WHERE user_id=? AND status NOT IN ('completed','cancelled') ORDER BY id DESC"
        else:
            q = "SELECT * FROM orders WHERE user_id=? AND status IN ('completed','cancelled') ORDER BY id DESC"
        cur = await db.execute(q, (user_id,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_active_orders() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM orders WHERE status NOT IN ('completed','cancelled') ORDER BY id DESC"
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_history_orders(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM orders WHERE status IN ('completed','cancelled') ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def search_orders(query: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        like = f"%{query}%"
        cur = await db.execute(
            """SELECT * FROM orders
               WHERE CAST(id AS TEXT)=? OR recipient_phone LIKE ? OR recipient_name LIKE ?
               ORDER BY id DESC""",
            (query, like, like),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()


async def set_delivery_price(order_id: int, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT items_total FROM orders WHERE id=?", (order_id,))
        row = await cur.fetchone()
        items_total = row[0] if row else 0
        new_total = items_total + price
        await db.execute(
            "UPDATE orders SET delivery_price=?, total=?, status='confirmed' WHERE id=?",
            (price, new_total, order_id),
        )
        await db.commit()
        return new_total


async def mark_order_paid(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET payment_status='paid' WHERE id=?", (order_id,))
        await db.commit()


# ---------- SETTINGS ----------

async def get_setting(key: str) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else ""


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        await db.commit()


async def get_all_settings() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT key, value FROM settings")
        rows = await cur.fetchall()
        return {k: v for k, v in rows}


# ---------- SUPPORT ----------

async def add_support_message(user_id: int, text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO support_messages (user_id, text, created_at) VALUES (?,?,?)",
            (user_id, text, int(time.time())),
        )
        await db.commit()
        return cur.lastrowid


# ---------- STATS ----------

async def get_sales_stats(since_ts: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as revenue
               FROM orders WHERE payment_status='paid' AND created_at>=?""",
            (since_ts,),
        )
        row = await cur.fetchone()
        paid_count, revenue = row["cnt"], row["revenue"]

        cur = await db.execute(
            "SELECT COUNT(*) FROM orders WHERE created_at>=?", (since_ts,)
        )
        total_orders = (await cur.fetchone())[0]

        cur = await db.execute(
            """SELECT oi.name_ru, SUM(oi.quantity) as qty, SUM(oi.price*oi.quantity) as revenue
               FROM order_items oi JOIN orders o ON o.id = oi.order_id
               WHERE o.payment_status='paid' AND o.created_at>=?
               GROUP BY oi.product_id ORDER BY qty DESC LIMIT 5""",
            (since_ts,),
        )
        top_products = [dict(r) for r in await cur.fetchall()]

        avg_check = int(revenue / paid_count) if paid_count else 0

        return {
            "total_orders": total_orders,
            "paid_orders": paid_count,
            "revenue": revenue,
            "avg_check": avg_check,
            "top_products": top_products,
        }
