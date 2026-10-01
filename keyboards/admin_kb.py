from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,
)
from db.database import SETTINGS_LABELS

ADMIN_BTN_ADD_PRODUCT = "➕ Добавить продукт / Mahsulot qo'shish"
ADMIN_BTN_EDIT_PRODUCT = "✏️ Редактировать / удалить / Tahrirlash-o'chirish"
ADMIN_BTN_ACTIVE_ORDERS = "📦 Актуальные заказы / Aktual buyurtmalar"
ADMIN_BTN_HISTORY_ORDERS = "🗃 Старые заказы / Eski buyurtmalar"
ADMIN_BTN_PAID = "💰 Оплаченные / To'langanlar"
ADMIN_BTN_BROADCAST = "📢 Рассылка / Post yuborish"
ADMIN_BTN_SETTINGS = "⚙️ Настройки / Sozlamalar"
ADMIN_BTN_STATS = "📊 Продажи / Sotuvlar"
ADMIN_BTN_EXPORT = "📥 Mijozlar ro'yxati"
ADMIN_BTN_PROMO = "🎟 Promo-kodlar"
ADMIN_BTN_STAFF = "👥 Xodimlar"
ADMIN_BTN_EXIT = "🚪 Выйти из админки / Admin panelidan chiqish"


def admin_main_menu_kb() -> ReplyKeyboardMarkup:
    """Eski nom - orqaga moslik uchun saqlangan, to'liq (admin) menyuni qaytaradi."""
    return admin_menu_kb_for_role("admin")


def admin_menu_kb_for_role(role: str) -> ReplyKeyboardMarkup:
    """Rolga qarab turlicha admin-panel menyusi.
    admin   - hammasi
    manager - mahsulot + buyurtmalar + mijozlar ro'yxati (sotuvchi)
    courier - faqat buyurtmalar (kuryer)
    """
    rows = []
    if role in ("admin", "manager"):
        rows.append([KeyboardButton(text=ADMIN_BTN_ADD_PRODUCT)])
        rows.append([KeyboardButton(text=ADMIN_BTN_EDIT_PRODUCT)])
    if role in ("admin", "manager", "courier"):
        rows.append([KeyboardButton(text=ADMIN_BTN_ACTIVE_ORDERS), KeyboardButton(text=ADMIN_BTN_HISTORY_ORDERS)])
    if role in ("admin", "manager"):
        rows.append([KeyboardButton(text=ADMIN_BTN_PAID), KeyboardButton(text=ADMIN_BTN_EXPORT)])
    if role == "admin":
        rows.append([KeyboardButton(text=ADMIN_BTN_BROADCAST)])
        rows.append([KeyboardButton(text=ADMIN_BTN_SETTINGS), KeyboardButton(text=ADMIN_BTN_STATS)])
        rows.append([KeyboardButton(text=ADMIN_BTN_PROMO), KeyboardButton(text=ADMIN_BTN_STAFF)])
    rows.append([KeyboardButton(text=ADMIN_BTN_EXIT)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def admin_categories_kb(categories: list[dict], prefix: str, with_add: bool = False) -> InlineKeyboardMarkup:
    rows = []
    for c in categories:
        rows.append([InlineKeyboardButton(
            text=f"{c['name_ru']} / {c['name_uz']}", callback_data=f"{prefix}:{c['id']}"
        )])
    if with_add:
        rows.append([InlineKeyboardButton(text="➕ Yangi kategoriya", callback_data=f"{prefix}:new")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_products_kb(products: list[dict], prefix: str) -> InlineKeyboardMarkup:
    rows = []
    for p in products:
        label = f"{p['name_ru']} — {p['price']:,}".replace(",", " ")
        rows.append([InlineKeyboardButton(text=label, callback_data=f"{prefix}:{p['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_old_price_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Пропустить / O'tkazib yuborish", callback_data="skip")]
    ])


def photo_extra_done_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Готово / Tayyor", callback_data="done")]
    ])


def availability_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ В наличии / Bor", callback_data="avail:1"),
            InlineKeyboardButton(text="❌ Нет / Yo'q", callback_data="avail:0"),
        ]
    ])


def add_product_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать / Chop etish", callback_data="publish")],
        [InlineKeyboardButton(text="❌ Отмена / Bekor qilish", callback_data="cancel_add")],
    ])


def edit_product_fields_kb(product_id: int) -> InlineKeyboardMarkup:
    fields = [
        ("name_ru", "Название RU"), ("name_uz", "Nomi UZ"),
        ("short_ru", "Кратко RU"), ("short_uz", "Qisqa UZ"),
        ("full_ru", "Описание RU"), ("full_uz", "Tavsif UZ"),
        ("price", "Цена / Narx"), ("old_price", "Старая цена / Eski narx"),
        ("photo_main", "Фото / Rasm"),
        ("characteristics_ru", "Характеристики RU"), ("characteristics_uz", "Xarakteristika UZ"),
    ]
    rows = [[InlineKeyboardButton(text=label, callback_data=f"editf:{product_id}:{key}")] for key, label in fields]
    rows.append([InlineKeyboardButton(text="👁 Показать/Скрыть / Ko'rsatish-yashirish", callback_data=f"toggle_hide:{product_id}")])
    rows.append([InlineKeyboardButton(text="🗑 Удалить / O'chirish", callback_data=f"delprod:{product_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_delete_kb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"delprod_confirm:{product_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="delprod_cancel"),
        ]
    ])


def order_actions_kb(order: dict) -> InlineKeyboardMarkup:
    rows = []
    status = order["status"]
    order_id = order["id"]

    if status == "pending" and order["city"] == "other" and order["delivery_price"] is None:
        rows.append([InlineKeyboardButton(text="💵 Yetkazish narxini belgilash", callback_data=f"setdeliv:{order_id}")])
    elif status == "shipped":
        rows.append([InlineKeyboardButton(text="⏳ Mijoz tasdiqlashini kutish...", callback_data="noop")])
    else:
        next_map = {
            "pending": ("✅ Tasdiqlash", "confirmed"),
            "confirmed": ("📦 Tayyorlashni boshlash", "preparing"),
            "preparing": ("🚚 Yetkazishga berish", "shipped"),
            "received": ("🏁 Yakunlash", "completed"),
        }
        if status in next_map:
            label, new_status = next_map[status]
            rows.append([InlineKeyboardButton(text=label, callback_data=f"setstatus:{order_id}:{new_status}")])

    if order["payment_status"] != "paid":
        rows.append([InlineKeyboardButton(text="💰 To'landi deb belgilash", callback_data=f"markpaid:{order_id}")])

    if status not in ("completed", "cancelled"):
        rows.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"setstatus:{order_id}:cancelled")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def broadcast_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Только текст / Faqat matn", callback_data="bc:text")],
        [InlineKeyboardButton(text="🖼 Фото + текст / Rasm + matn", callback_data="bc:photo")],
        [InlineKeyboardButton(text="🎥 Видео + текст / Video + matn", callback_data="bc:video")],
    ])


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить всем / Hammaga yuborish", callback_data="bc_send")],
        [InlineKeyboardButton(text="❌ Отмена / Bekor qilish", callback_data="bc_cancel")],
    ])


def settings_kb() -> InlineKeyboardMarkup:
    rows = []
    for key, label in SETTINGS_LABELS.items():
        rows.append([InlineKeyboardButton(text=f"{label['ru']} / {label['uz']}", callback_data=f"setkey:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def stats_period_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Bugun", callback_data="stats:1"),
            InlineKeyboardButton(text="7 kun", callback_data="stats:7"),
            InlineKeyboardButton(text="30 kun", callback_data="stats:30"),
        ]
    ])


def support_reply_kb(support_msg_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ответить / Javob berish", callback_data=f"supreply:{support_msg_id}:{user_id}")]
    ])


def staff_list_kb(staff: list[dict]) -> InlineKeyboardMarkup:
    role_names = {"manager": "Sotuvchi", "courier": "Kuryer"}
    rows = [
        [InlineKeyboardButton(
            text=f"🗑 {s['tg_id']} — {role_names.get(s['role'], s['role'])}",
            callback_data=f"staffdel:{s['tg_id']}",
        )]
        for s in staff
    ]
    rows.append([InlineKeyboardButton(text="➕ Yangi xodim qo'shish", callback_data="staff_add")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def staff_role_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Sotuvchi (mahsulot + buyurtma)", callback_data="staffrole:manager")],
        [InlineKeyboardButton(text="🚚 Kuryer (faqat buyurtma)", callback_data="staffrole:courier")],
    ])


def promo_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi promo-kod yaratish", callback_data="promo_new")],
        [InlineKeyboardButton(text="📋 Ro'yxat", callback_data="promo_list")],
    ])


def promo_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="% Foizli chegirma", callback_data="promotype:percent")],
        [InlineKeyboardButton(text="💰 Belgilangan summa", callback_data="promotype:fixed")],
    ])


def promo_skip_maxuses_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♾️ Cheksiz (o'tkazib yuborish)", callback_data="promo_skip_maxuses")]
    ])


def promo_list_kb(promos: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for p in promos:
        status = "✅" if p["active"] else "🚫"
        usage = f"{p['used_count']}/{p['max_uses']}" if p["max_uses"] else f"{p['used_count']}/∞"
        value = f"{p['discount_value']}%" if p["discount_type"] == "percent" else f"{p['discount_value']:,}".replace(",", " ")
        label = f"{status} {p['code']} — {value} ({usage})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"promotoggle:{p['code']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
