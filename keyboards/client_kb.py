from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,
)
from utils.texts import t


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz")],
    ])


def phone_request_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("share_contact_btn", lang), request_contact=True)]],
        resize_keyboard=True,
    )


def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_catalog", lang)), KeyboardButton(text=t("btn_cart", lang))],
            [KeyboardButton(text=t("btn_orders", lang)), KeyboardButton(text=t("btn_about", lang))],
            [KeyboardButton(text=t("btn_support", lang))],
        ],
        resize_keyboard=True,
    )


def categories_kb(categories: list[dict], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for c in categories:
        name = c["name_ru"] if lang == "ru" else c["name_uz"]
        rows.append([InlineKeyboardButton(text=name, callback_data=f"cat:{c['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def products_kb(products: list[dict], lang: str, cat_id: int) -> InlineKeyboardMarkup:
    rows = []
    for p in products:
        name = p["name_ru"] if lang == "ru" else p["name_uz"]
        price = f"{p['price']:,}".replace(",", " ")
        rows.append([InlineKeyboardButton(text=f"{name} — {price}", callback_data=f"prod:{p['id']}")])
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="cat:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_card_kb(product_id: int, cat_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("add_to_cart_btn", lang), callback_data=f"addcart:{product_id}")],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data=f"cat:{cat_id}")],
    ])


def cart_kb(cart: list[dict], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for item in cart:
        name = item["name_ru"] if lang == "ru" else item["name_uz"]
        rows.append([InlineKeyboardButton(text=f"{name[:20]} x{item['quantity']}", callback_data="noop")])
        rows.append([
            InlineKeyboardButton(text="➖", callback_data=f"cartminus:{item['cart_item_id']}"),
            InlineKeyboardButton(text=str(item["quantity"]), callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cartplus:{item['cart_item_id']}"),
            InlineKeyboardButton(text="🗑", callback_data=f"cartdel:{item['cart_item_id']}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cart_actions_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("checkout_btn", lang))],
            [KeyboardButton(text=t("continue_shopping_btn", lang))],
            [KeyboardButton(text=t("clear_cart_btn", lang))],
        ],
        resize_keyboard=True,
    )


def city_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("city_tashkent", lang))],
            [KeyboardButton(text=t("city_other", lang))],
            [KeyboardButton(text=t("btn_cancel", lang))],
        ],
        resize_keyboard=True,
    )


def location_or_skip_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("send_location_btn", lang), request_location=True)],
            [KeyboardButton(text=t("btn_cancel", lang))],
        ],
        resize_keyboard=True,
    )


def skip_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_skip", lang))]], resize_keyboard=True
    )


def confirm_order_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("confirm_order_btn", lang), callback_data="order_confirm")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="order_cancel")],
    ])


def orders_tabs_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("orders_tab_active", lang), callback_data="orders:active"),
            InlineKeyboardButton(text=t("orders_tab_history", lang), callback_data="orders:history"),
        ]
    ])


def remove_kb() -> ReplyKeyboardMarkup:
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
