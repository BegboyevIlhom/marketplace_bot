"""
Admin-panel menyu va asosiy tugma matnlari - RU/UZ alohida.
Har bir admin/xodim o'zining (ro'yxatdan o'tishda tanlagan) tilida
to'liq bir xil tilda ko'radigan panelga ega bo'lishi uchun.
"""

ADMIN_TEXTS = {
    "btn_add_product": {"ru": "➕ Добавить продукт", "uz": "➕ Mahsulot qo'shish"},
    "btn_edit_product": {"ru": "✏️ Редактировать / удалить", "uz": "✏️ Tahrirlash / o'chirish"},
    "btn_view_products": {"ru": "📋 Список товаров", "uz": "📋 Mahsulotlar ro'yxati"},
    "btn_active_orders": {"ru": "📦 Активные заказы", "uz": "📦 Aktual buyurtmalar"},
    "btn_history_orders": {"ru": "🗃 Старые заказы", "uz": "🗃 Eski buyurtmalar"},
    "btn_paid": {"ru": "💰 Оплаченные", "uz": "💰 To'langanlar"},
    "btn_broadcast": {"ru": "📢 Рассылка", "uz": "📢 Post yuborish"},
    "btn_settings": {"ru": "⚙️ Настройки", "uz": "⚙️ Sozlamalar"},
    "btn_stats": {"ru": "📊 Продажи", "uz": "📊 Sotuvlar"},
    "btn_mystats": {"ru": "👤 Моя статистика", "uz": "👤 Mening statistikam"},
    "btn_export": {"ru": "📥 Клиенты", "uz": "📥 Mijozlar ro'yxati"},
    "btn_promo": {"ru": "🎟 Промокоды", "uz": "🎟 Promo-kodlar"},
    "btn_staff": {"ru": "👥 Сотрудники", "uz": "👥 Xodimlar"},
    "btn_set_pin": {"ru": "🔒 PIN-код", "uz": "🔒 PIN-kod"},
    "btn_exit": {"ru": "🚪 Выйти из админки", "uz": "🚪 Admin panelidan chiqish"},

    "pin_ask": {"ru": "🔒 Введите PIN-код:", "uz": "🔒 PIN-kodni kiriting:"},
    "pin_wrong": {"ru": "❌ Неверный PIN. Повторите:", "uz": "❌ Noto'g'ri PIN. Qayta kiriting:"},
    "pin_ok": {"ru": "✅ Доступ подтверждён", "uz": "✅ Kirish tasdiqlandi"},
    "pin_set_ask_new": {
        "ru": "Введите новый 4-значный PIN-код:", "uz": "Yangi 4 xonali PIN-kodni kiriting:"
    },
    "pin_set_ask_confirm": {
        "ru": "Повторите PIN-код для подтверждения:", "uz": "Tasdiqlash uchun PIN-kodni qayta kiriting:"
    },
    "pin_set_wrong_format": {
        "ru": "PIN должен состоять ровно из 4 цифр. Повторите:",
        "uz": "PIN aynan 4 ta raqamdan iborat bo'lishi kerak. Qayta kiriting:",
    },
    "pin_set_mismatch": {
        "ru": "PIN-коды не совпали. Начните заново:", "uz": "PIN-kodlar mos kelmadi. Qaytadan boshlang:"
    },
    "pin_set_done": {"ru": "✅ PIN-код сохранён", "uz": "✅ PIN-kod saqlandi"},

    "mystats_title": {"ru": "👤 Ваша статистика:", "uz": "👤 Sizning statistikangiz:"},
    "mystats_products": {"ru": "Добавлено товаров", "uz": "Qo'shgan mahsulotlaringiz"},
    "mystats_orders": {"ru": "Завершено заказов", "uz": "Yakunlagan buyurtmalaringiz"},
}


def at(key: str, lang: str) -> str:
    d = ADMIN_TEXTS.get(key, {})
    return d.get(lang) or d.get("ru") or key


def all_variants(key: str) -> list:
    d = ADMIN_TEXTS.get(key, {})
    return [v for v in (d.get("ru"), d.get("uz")) if v]
