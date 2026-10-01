from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import db.database as db
from utils.texts import t
from keyboards.client_kb import cart_kb, cart_actions_kb, main_menu_kb

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


def _cart_text(cart: list[dict], lang: str) -> str:
    lines = [t("cart_title", lang), ""]
    total = 0
    for i, item in enumerate(cart, 1):
        name = item["name_ru"] if lang == "ru" else item["name_uz"]
        line_total = item["price"] * item["quantity"]
        total += line_total
        price = f"{item['price']:,}".replace(",", " ")
        lt = f"{line_total:,}".replace(",", " ")
        lines.append(f"{i}. {name} — {item['quantity']} x {price} = {lt}")
    lines.append("")
    lines.append(f"{t('cart_total', lang)}: {total:,}".replace(",", " "))
    return "\n".join(lines)


@router.message(F.text.in_(["🛒 Корзина", "🛒 Savat"]))
async def show_cart(message: Message):
    lang = await _lang(message.from_user.id)
    user = await db.get_or_create_user(message.from_user.id)
    cart = await db.get_cart(user["id"])
    if not cart:
        await message.answer(t("cart_empty", lang))
        return
    await message.answer(_cart_text(cart, lang), reply_markup=cart_kb(cart, lang))
    await message.answer(t("main_menu_client", lang), reply_markup=cart_actions_kb(lang))


@router.callback_query(F.data.startswith("cartplus:"))
async def cart_plus(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    cart_item_id = int(callback.data.split(":")[1])
    await db.update_cart_qty(cart_item_id, 1)
    user = await db.get_or_create_user(callback.from_user.id)
    cart = await db.get_cart(user["id"])
    if cart:
        await callback.message.edit_text(_cart_text(cart, lang), reply_markup=cart_kb(cart, lang))
    else:
        await callback.message.edit_text(t("cart_empty", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("cartminus:"))
async def cart_minus(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    cart_item_id = int(callback.data.split(":")[1])
    await db.update_cart_qty(cart_item_id, -1)
    user = await db.get_or_create_user(callback.from_user.id)
    cart = await db.get_cart(user["id"])
    if cart:
        await callback.message.edit_text(_cart_text(cart, lang), reply_markup=cart_kb(cart, lang))
    else:
        await callback.message.edit_text(t("cart_empty", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("cartdel:"))
async def cart_del(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    cart_item_id = int(callback.data.split(":")[1])
    await db.remove_cart_item(cart_item_id)
    user = await db.get_or_create_user(callback.from_user.id)
    cart = await db.get_cart(user["id"])
    if cart:
        await callback.message.edit_text(_cart_text(cart, lang), reply_markup=cart_kb(cart, lang))
    else:
        await callback.message.edit_text(t("cart_empty", lang))
    await callback.answer()


@router.message(F.text.in_(["🧹 Очистить корзину", "🧹 Savatni tozalash"]))
async def clear_cart(message: Message):
    lang = await _lang(message.from_user.id)
    user = await db.get_or_create_user(message.from_user.id)
    await db.clear_cart(user["id"])
    await message.answer(t("cart_cleared", lang), reply_markup=main_menu_kb(lang))


@router.message(F.text.in_(["🛍 Продолжить покупки", "🛍 Xaridni davom ettirish"]))
async def continue_shopping(message: Message):
    lang = await _lang(message.from_user.id)
    await message.answer(t("main_menu_client", lang), reply_markup=main_menu_kb(lang))


@router.callback_query(F.data == "view_cart_from_reminder")
async def view_cart_from_reminder(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    user = await db.get_or_create_user(callback.from_user.id)
    cart = await db.get_cart(user["id"])
    if not cart:
        await callback.message.answer(t("cart_empty", lang))
    else:
        await callback.message.answer(_cart_text(cart, lang), reply_markup=cart_kb(cart, lang))
        await callback.message.answer(t("main_menu_client", lang), reply_markup=cart_actions_kb(lang))
    await callback.answer()
