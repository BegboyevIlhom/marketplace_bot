from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
import json

import db.database as db
from utils.texts import t
from keyboards.client_kb import categories_kb, products_kb, product_card_kb

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(F.text.in_(["🛍 Каталог", "🛍 Katalog"]))
async def show_catalog(message: Message):
    lang = await _lang(message.from_user.id)
    categories = await db.get_categories()
    if not categories:
        await message.answer(t("no_categories", lang))
        return
    await message.answer(t("choose_category", lang), reply_markup=categories_kb(categories, lang))


@router.callback_query(F.data == "cat:back")
async def back_to_categories(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    categories = await db.get_categories()
    await callback.message.edit_text(t("choose_category", lang), reply_markup=categories_kb(categories, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    cat_id = int(callback.data.split(":")[1])
    products = await db.get_products_by_category(cat_id)
    if not products:
        await callback.answer(t("no_products", lang), show_alert=True)
        return
    await callback.message.edit_text(t("choose_product", lang), reply_markup=products_kb(products, lang, cat_id))
    await callback.answer()


@router.callback_query(F.data.startswith("catsort:"))
async def sort_products(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    _, cat_id, sort = callback.data.split(":")
    cat_id = int(cat_id)
    products = await db.get_products_by_category(cat_id, sort=sort)
    if not products:
        await callback.answer(t("no_products", lang), show_alert=True)
        return
    await callback.message.edit_text(
        t("choose_product", lang), reply_markup=products_kb(products, lang, cat_id, sort)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product_card(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    product_id = int(callback.data.split(":")[1])
    p = await db.get_product(product_id)
    if not p or p["is_deleted"] or p["is_hidden"]:
        await callback.answer(t("no_products", lang), show_alert=True)
        return

    user = await db.get_or_create_user(callback.from_user.id)
    is_fav = await db.is_favorite(user["id"], product_id)

    name = p["name_ru"] if lang == "ru" else p["name_uz"]
    short = p["short_ru"] if lang == "ru" else p["short_uz"]
    full = p["full_ru"] if lang == "ru" else p["full_uz"]
    chars = p["characteristics_ru"] if lang == "ru" else p["characteristics_uz"]
    price = f"{p['price']:,}".replace(",", " ")

    text = f"📦 <b>{name}</b>\n\n{short}\n\n{full}"
    if chars:
        text += f"\n\n🔧 {chars}"
    if p["old_price"]:
        old_price = f"{p['old_price']:,}".replace(",", " ")
        text += f"\n\n<s>{old_price}</s> 💰 <b>{price}</b>"
    else:
        text += f"\n\n💰 <b>{price}</b>"
    text += f"\n{t('available', lang) if p['available'] else t('not_available', lang)}"

    kb = product_card_kb(product_id, p["category_id"], lang, is_fav=is_fav)
    extra_photos = json.loads(p["photos_extra"] or "[]")

    if extra_photos:
        # Bir nechta rasm bo'lsa - albom (media group) sifatida yuboriladi.
        # Telegram media group'ga tugma (reply_markup) biriktirib bo'lmaydi,
        # shuning uchun tugmalar alohida, qisqa xabarda yuboriladi.
        media = [InputMediaPhoto(media=p["photo_main"], caption=text, parse_mode="HTML")]
        for file_id in extra_photos[:9]:
            media.append(InputMediaPhoto(media=file_id))
        await callback.message.answer_media_group(media)
        await callback.message.answer(name, reply_markup=kb)
        await callback.message.delete()
    elif p["photo_main"]:
        await callback.message.answer_photo(p["photo_main"], caption=text, reply_markup=kb, parse_mode="HTML")
        await callback.message.delete()
    else:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("favadd:"))
async def add_favorite_cb(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    product_id = int(callback.data.split(":")[1])
    user = await db.get_or_create_user(callback.from_user.id)
    await db.add_favorite(user["id"], product_id)
    p = await db.get_product(product_id)
    if p:
        kb = product_card_kb(product_id, p["category_id"], lang, is_fav=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=kb)
        except Exception:
            pass
    await callback.answer(t("added_to_favorites", lang))


@router.callback_query(F.data.startswith("favdel:"))
async def remove_favorite_cb(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    product_id = int(callback.data.split(":")[1])
    user = await db.get_or_create_user(callback.from_user.id)
    await db.remove_favorite(user["id"], product_id)
    p = await db.get_product(product_id)
    if p:
        kb = product_card_kb(product_id, p["category_id"], lang, is_fav=False)
        try:
            await callback.message.edit_reply_markup(reply_markup=kb)
        except Exception:
            pass
    await callback.answer(t("removed_from_favorites", lang))


@router.callback_query(F.data.startswith("addcart:"))
async def add_to_cart_cb(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    product_id = int(callback.data.split(":")[1])
    p = await db.get_product(product_id)
    if not p or not p["available"] or p["is_deleted"] or p["is_hidden"]:
        await callback.answer(t("not_available", lang), show_alert=True)
        return
    user = await db.get_or_create_user(callback.from_user.id)
    await db.add_to_cart(user["id"], product_id, 1)
    await callback.answer(t("added_to_cart", lang))
