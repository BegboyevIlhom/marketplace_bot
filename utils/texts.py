"""
Botning barcha matnlari shu yerda, RU/UZ ikki tilda.
Yangi matn qo'shish kerak bo'lsa - shu faylga TEXTS lug'atiga qo'shiladi.
"""

TEXTS = {
    "choose_language": {
        "ru": "Добро пожаловать! 👋\nВыберите язык:",
        "uz": "Xush kelibsiz! 👋\nTilni tanlang:",
    },
    "ask_phone": {
        "ru": "Для завершения регистрации отправьте, пожалуйста, свой номер телефона:",
        "uz": "Ro'yxatdan o'tishni yakunlash uchun telefon raqamingizni yuboring:",
    },
    "share_contact_btn": {"ru": "📱 Поделиться контактом", "uz": "📱 Kontaktni ulashish"},
    "registered": {
        "ru": "Регистрация завершена ✅",
        "uz": "Ro'yxatdan o'tish yakunlandi ✅",
    },
    "main_menu_client": {
        "ru": "Главное меню:",
        "uz": "Asosiy menyu:",
    },
    "btn_catalog": {"ru": "🛍 Каталог", "uz": "🛍 Katalog"},
    "btn_cart": {"ru": "🛒 Корзина", "uz": "🛒 Savat"},
    "btn_orders": {"ru": "📦 Заказы", "uz": "📦 Buyurtmalar"},
    "btn_about": {"ru": "ℹ️ О нас", "uz": "ℹ️ Biz haqimizda"},
    "btn_support": {"ru": "💬 Связаться с админом", "uz": "💬 Admin bilan bog'lanish"},
    "btn_back": {"ru": "⬅️ Назад", "uz": "⬅️ Orqaga"},
    "btn_cancel": {"ru": "❌ Отмена", "uz": "❌ Bekor qilish"},
    "btn_skip": {"ru": "➡️ Пропустить", "uz": "➡️ O'tkazib yuborish"},
    "btn_done": {"ru": "✅ Готово", "uz": "✅ Tayyor"},

    "choose_category": {"ru": "Выберите категорию:", "uz": "Kategoriyani tanlang:"},
    "no_categories": {"ru": "Пока нет категорий.", "uz": "Hozircha kategoriyalar yo'q."},
    "choose_product": {"ru": "Товары в категории:", "uz": "Kategoriyadagi tovarlar:"},
    "no_products": {"ru": "В этой категории пока нет товаров.", "uz": "Bu kategoriyada hozircha tovar yo'q."},
    "add_to_cart_btn": {"ru": "🛒 В корзину", "uz": "🛒 Savatga qo'shish"},
    "added_to_cart": {"ru": "Товар добавлен в корзину ✅", "uz": "Tovar savatga qo'shildi ✅"},
    "not_available": {"ru": "❌ Нет в наличии", "uz": "❌ Sotuvda yo'q"},
    "available": {"ru": "✅ В наличии", "uz": "✅ Sotuvda bor"},

    "cart_empty": {"ru": "Ваша корзина пуста 🛒", "uz": "Savatingiz bo'sh 🛒"},
    "cart_title": {"ru": "🛒 Ваша корзина:", "uz": "🛒 Sizning savatingiz:"},
    "cart_total": {"ru": "Итого", "uz": "Jami"},
    "continue_shopping_btn": {"ru": "🛍 Продолжить покупки", "uz": "🛍 Xaridni davom ettirish"},
    "checkout_btn": {"ru": "✅ Оформить заказ", "uz": "✅ Buyurtma berish"},
    "clear_cart_btn": {"ru": "🧹 Очистить корзину", "uz": "🧹 Savatni tozalash"},
    "cart_cleared": {"ru": "Корзина очищена.", "uz": "Savat tozalandi."},
    "price_changed_warning": {
        "ru": "⚠️ Цена или наличие некоторых товаров изменились. Проверьте корзину.",
        "uz": "⚠️ Ba'zi tovarlarning narxi yoki mavjudligi o'zgargan. Savatni tekshiring.",
    },

    "checkout_ask_name": {"ru": "Введите имя получателя:", "uz": "Qabul qiluvchining ismini kiriting:"},
    "checkout_use_saved_name_btn": {"ru": "Использовать {name}", "uz": "{name}dan foydalanish"},
    "checkout_ask_city": {"ru": "Выберите город доставки:", "uz": "Yetkazib berish shahrini tanlang:"},
    "city_tashkent": {"ru": "Ташкент", "uz": "Toshkent"},
    "city_other": {"ru": "Другой регион", "uz": "Boshqa hudud"},
    "checkout_ask_address": {
        "ru": "Введите адрес доставки текстом, или отправьте геолокацию кнопкой ниже:",
        "uz": "Yetkazib berish manzilini matn ko'rinishida kiriting, yoki quyidagi tugma orqali lokatsiya yuboring:",
    },
    "send_location_btn": {"ru": "📍 Отправить локацию", "uz": "📍 Lokatsiya yuborish"},
    "checkout_ask_comment": {
        "ru": "Есть комментарий или ориентир к адресу? Если нет — нажмите «Пропустить».",
        "uz": "Manzilga izoh yoki mo'ljal bormi? Bo'lmasa «O'tkazib yuborish»ni bosing.",
    },
    "checkout_other_region_note": {
        "ru": "Стоимость доставки для вашего региона будет согласована с администратором. Вы получите уведомление с итоговой суммой.",
        "uz": "Sizning hududingiz uchun yetkazib berish narxi administrator bilan kelishiladi. Yakuniy summa haqida xabar olasiz.",
    },
    "checkout_confirm_title": {"ru": "Проверьте ваш заказ:", "uz": "Buyurtmangizni tekshiring:"},
    "confirm_order_btn": {"ru": "✅ Подтвердить заказ", "uz": "✅ Buyurtmani tasdiqlash"},
    "order_created": {
        "ru": "Заказ №{order_id} создан ✅\nСумма: {total}",
        "uz": "№{order_id} raqamli buyurtma yaratildi ✅\nSumma: {total}",
    },
    "order_created_pending_delivery": {
        "ru": "Заказ №{order_id} принят. Мы свяжемся с вами для уточнения стоимости доставки.",
        "uz": "№{order_id} raqamli buyurtma qabul qilindi. Yetkazib berish narxini aniqlashtirish uchun siz bilan bog'lanamiz.",
    },
    "delivery_cost": {"ru": "Доставка", "uz": "Yetkazib berish"},
    "delivery_pending": {"ru": "уточняется", "uz": "aniqlashtirilmoqda"},
    "free": {"ru": "бесплатно", "uz": "bepul"},

    "orders_tab_active": {"ru": "Актуальные", "uz": "Aktual"},
    "orders_tab_history": {"ru": "История", "uz": "Tarix"},
    "no_orders": {"ru": "Заказов пока нет.", "uz": "Hozircha buyurtmalar yo'q."},

    "support_ask_question": {
        "ru": "Опишите ваш вопрос одним сообщением:",
        "uz": "Savolingizni bitta xabarda yozing:",
    },
    "support_sent": {
        "ru": "Ваш вопрос отправлен администратору. Мы ответим в ближайшее время.",
        "uz": "Savolingiz administratorga yuborildi. Tez orada javob beramiz.",
    },
    "support_admin_notify": {
        "ru": "💬 Новый вопрос от клиента\nИмя: {name}\nТелефон: {phone}\n\n{text}",
        "uz": "💬 Mijozdan yangi savol\nIsmi: {name}\nTelefon: {phone}\n\n{text}",
    },
    "support_reply_btn": {"ru": "✏️ Ответить", "uz": "✏️ Javob berish"},
    "support_ask_reply": {"ru": "Введите ответ клиенту:", "uz": "Mijozga javobni kiriting:"},
    "support_reply_sent_to_client": {"ru": "💬 Ответ администратора:\n\n{text}", "uz": "💬 Administrator javobi:\n\n{text}"},
    "support_reply_confirmed": {"ru": "Ответ отправлен клиенту ✅", "uz": "Javob mijozga yuborildi ✅"},

    "status_pending": {"ru": "🕓 Ожидает подтверждения", "uz": "🕓 Tasdiqlash kutilmoqda"},
    "status_confirmed": {"ru": "✅ Подтвержден", "uz": "✅ Tasdiqlandi"},
    "status_preparing": {"ru": "📦 Собирается", "uz": "📦 Tayyorlanmoqda"},
    "status_shipped": {"ru": "🚚 Передан в доставку", "uz": "🚚 Yetkazishga berildi"},
    "status_received": {"ru": "📥 Клиент получил заказ", "uz": "📥 Mijoz qabul qildi"},
    "status_completed": {"ru": "🏁 Завершен", "uz": "🏁 Yakunlandi"},
    "status_cancelled": {"ru": "❌ Отменен", "uz": "❌ Bekor qilindi"},

    "status_changed_notify": {
        "ru": "Статус вашего заказа №{order_id} изменен:\n{status}",
        "uz": "№{order_id} raqamli buyurtmangiz statusi o'zgardi:\n{status}",
    },
    "delivery_price_set_notify": {
        "ru": "Стоимость доставки для заказа №{order_id} установлена: {price}\nИтоговая сумма: {total}",
        "uz": "№{order_id} buyurtma uchun yetkazib berish narxi belgilandi: {price}\nYakuniy summa: {total}",
    },
    "paid_notify": {
        "ru": "Оплата по заказу №{order_id} подтверждена ✅",
        "uz": "№{order_id} buyurtma bo'yicha to'lov tasdiqlandi ✅",
    },
    "confirm_receipt_btn": {"ru": "✅ Я получил заказ", "uz": "✅ Men qabul qildim"},
    "receipt_confirmed_client": {
        "ru": "Спасибо! Подтверждение получено ✅",
        "uz": "Rahmat! Tasdiqlandi ✅",
    },

    "btn_search": {"ru": "🔍 Поиск", "uz": "🔍 Qidiruv"},
    "search_ask": {"ru": "Введите название товара:", "uz": "Mahsulot nomini kiriting:"},
    "search_no_results": {"ru": "Ничего не найдено 😔", "uz": "Hech narsa topilmadi 😔"},
    "search_results_title": {"ru": "Результаты поиска:", "uz": "Qidiruv natijalari:"},

    "btn_favorites": {"ru": "❤️ Избранное", "uz": "❤️ Sevimlilar"},
    "add_favorite_btn": {"ru": "❤️ В избранное", "uz": "❤️ Sevimlilarga qo'shish"},
    "remove_favorite_btn": {"ru": "💔 Убрать из избранного", "uz": "💔 Sevimlilardan olib tashlash"},
    "added_to_favorites": {"ru": "Добавлено в избранное ❤️", "uz": "Sevimlilarga qo'shildi ❤️"},
    "removed_from_favorites": {"ru": "Убрано из избранного", "uz": "Sevimlilardan olib tashlandi"},
    "favorites_empty": {"ru": "Список избранного пуст", "uz": "Sevimlilar ro'yxati bo'sh"},
    "favorites_title": {"ru": "❤️ Ваше избранное:", "uz": "❤️ Sevimlilaringiz:"},

    "cart_reminder_text": {
        "ru": "Вы оставили товары в корзине 🛒\nНе забудьте оформить заказ!",
        "uz": "Siz savatda mahsulot qoldirgansiz 🛒\nBuyurtma berishni unutmang!",
    },
    "view_cart_btn": {"ru": "🛒 Открыть корзину", "uz": "🛒 Savatni ochish"},

    "reorder_btn": {"ru": "🔁 Повторить заказ", "uz": "🔁 Qayta buyurtma"},
    "reorder_done": {
        "ru": "Добавлено в корзину: {added}\nНедоступно: {skipped}",
        "uz": "Savatga qo'shildi: {added}\nMavjud emas: {skipped}",
    },

    "checkout_ask_promo": {
        "ru": "Есть промокод? Если нет — нажмите «Пропустить».",
        "uz": "Promo-kodingiz bormi? Bo'lmasa «O'tkazib yuborish»ni bosing.",
    },
    "promo_invalid": {
        "ru": "Промокод недействителен. Попробуйте другой или нажмите «Пропустить».",
        "uz": "Promo-kod yaroqsiz. Boshqasini urinib ko'ring yoki «O'tkazib yuborish»ni bosing.",
    },
    "promo_applied": {
        "ru": "Промокод применён! Скидка: {discount}",
        "uz": "Promo-kod qo'llandi! Chegirma: {discount}",
    },
    "discount_label": {"ru": "Скидка", "uz": "Chegirma"},
}


def t(key: str, lang: str, **kwargs) -> str:
    value = TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("ru", key))
    if kwargs:
        return value.format(**kwargs)
    return value


STATUS_KEYS = {
    "pending": "status_pending",
    "confirmed": "status_confirmed",
    "preparing": "status_preparing",
    "shipped": "status_shipped",
    "received": "status_received",
    "completed": "status_completed",
    "cancelled": "status_cancelled",
}


def status_text(status: str, lang: str) -> str:
    return t(STATUS_KEYS.get(status, "status_pending"), lang)
