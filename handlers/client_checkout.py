from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from utils.states import Checkout
from utils.texts import t
from keyboards.client_kb import (
    city_kb, location_or_skip_kb, skip_kb, confirm_order_kb, main_menu_kb,
)
from config import ADMIN_IDS

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(F.text.in_(["✅ Оформить заказ", "✅ Buyurtma berish"]))
async def start_checkout(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    user = await db.get_or_create_user(message.from_user.id)
    cart = await db.get_cart(user["id"])
    if not cart:
        await message.answer(t("cart_empty", lang), reply_markup=main_menu_kb(lang))
        return

    # Checkout oldidan narx/mavjudlikni qayta tekshirish
    for item in cart:
        fresh = await db.get_product(item["id"])
        if not fresh or not fresh["available"] or fresh["is_deleted"] or fresh["is_hidden"]:
            await message.answer(t("price_changed_warning", lang), reply_markup=main_menu_kb(lang))
            return

    await state.update_data(name=user["name"] or "")
    await message.answer(t("checkout_ask_name", lang), reply_markup=skip_kb(lang) if user["name"] else None)
    await state.set_state(Checkout.name)


@router.message(Checkout.name)
async def checkout_name(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    name = message.text
    if name in (t("btn_skip", "ru"), t("btn_skip", "uz")):
        data = await state.get_data()
        name = data.get("name", "")
    await state.update_data(name=name)
    await message.answer(t("checkout_ask_city", lang), reply_markup=city_kb(lang))
    await state.set_state(Checkout.city)


@router.message(Checkout.city)
async def checkout_city(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    if message.text == t("btn_cancel", lang):
        await state.clear()
        await message.answer(t("main_menu_client", lang), reply_markup=main_menu_kb(lang))
        return

    if message.text == t("city_tashkent", lang):
        await state.update_data(city="tashkent")
    elif message.text == t("city_other", lang):
        await state.update_data(city="other")
    else:
        await message.answer(t("checkout_ask_city", lang), reply_markup=city_kb(lang))
        return

    await message.answer(t("checkout_ask_address", lang), reply_markup=location_or_skip_kb(lang))
    await state.set_state(Checkout.address)


@router.message(Checkout.address, F.location)
async def checkout_address_location(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    await state.update_data(
        address="📍 Геолокация" if lang == "ru" else "📍 Lokatsiya",
        lat=message.location.latitude,
        lon=message.location.longitude,
    )
    await message.answer(t("checkout_ask_comment", lang), reply_markup=skip_kb(lang))
    await state.set_state(Checkout.comment)


@router.message(Checkout.address, F.text)
async def checkout_address_text(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    if message.text == t("btn_cancel", lang):
        await state.clear()
        await message.answer(t("main_menu_client", lang), reply_markup=main_menu_kb(lang))
        return
    await state.update_data(address=message.text, lat=None, lon=None)
    await message.answer(t("checkout_ask_comment", lang), reply_markup=skip_kb(lang))
    await state.set_state(Checkout.comment)


@router.message(Checkout.comment)
async def checkout_comment(message: Message, state: FSMContext, bot: Bot):
    lang = await _lang(message.from_user.id)
    comment = "" if message.text == t("btn_skip", lang) else message.text
    await state.update_data(comment=comment)
    data = await state.get_data()

    user = await db.get_or_create_user(message.from_user.id)
    cart = await db.get_cart(user["id"])
    items_total = sum(i["price"] * i["quantity"] for i in cart)

    delivery_price = None
    delivery_line = t("delivery_pending", lang)
    if data["city"] == "tashkent":
        delivery_price = int(await db.get_setting("delivery_price_tashkent"))
        threshold = int(await db.get_setting("free_delivery_threshold") or 0)
        if threshold and items_total >= threshold:
            delivery_price = 0
            delivery_line = t("free", lang)
        else:
            delivery_line = f"{delivery_price:,}".replace(",", " ")

    total = items_total + (delivery_price or 0)

    lines = [t("checkout_confirm_title", lang), ""]
    for i, item in enumerate(cart, 1):
        name = item["name_ru"] if lang == "ru" else item["name_uz"]
        lines.append(f"{i}. {name} x{item['quantity']}")
    lines.append("")
    lines.append(f"{t('cart_total', lang)}: {items_total:,}".replace(",", " "))
    lines.append(f"{t('delivery_cost', lang)}: {delivery_line}")
    if delivery_price is not None:
        lines.append(f"= {total:,}".replace(",", " "))
    else:
        lines.append(t("checkout_other_region_note", lang))
    lines.append("")
    lines.append(f"👤 {data['name']}")
    lines.append(f"📍 {data['address']}")
    if comment:
        lines.append(f"💬 {comment}")

    await state.update_data(delivery_price=delivery_price, items_total=items_total, total=total)
    await message.answer("\n".join(lines), reply_markup=confirm_order_kb(lang))
    await state.set_state(Checkout.confirm)


@router.callback_query(Checkout.confirm, F.data == "order_confirm")
async def checkout_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    lang = await _lang(callback.from_user.id)
    data = await state.get_data()
    user = await db.get_or_create_user(callback.from_user.id)
    cart = await db.get_cart(user["id"])

    if not cart:
        await callback.message.edit_text(t("cart_empty", lang))
        await state.clear()
        return

    order = await db.create_order(
        user_id=user["id"],
        cart=cart,
        city=data["city"],
        delivery_price=data["delivery_price"],
        address=data["address"],
        lat=data.get("lat"),
        lon=data.get("lon"),
        comment=data.get("comment", ""),
        recipient_name=data["name"],
        recipient_phone=user["phone"],
    )
    await db.clear_cart(user["id"])
    await state.clear()

    if data["delivery_price"] is None:
        text = t("order_created_pending_delivery", lang, order_id=order["id"])
    else:
        total = f"{order['total']:,}".replace(",", " ")
        payment_info = await db.get_setting("payment_info")
        text = t("order_created", lang, order_id=order["id"], total=total) + f"\n\n{payment_info}"

    await callback.message.edit_text(text)
    await callback.message.answer(t("main_menu_client", lang), reply_markup=main_menu_kb(lang))

    # Adminlarga xabar
    admin_text = (
        f"🆕 Yangi buyurtma №{order['id']}\n"
        f"Mijoz: {data['name']} ({user['phone']})\n"
        f"Manzil: {data['address']}"
    )
    if data.get("lat"):
        admin_text += f"\nhttps://maps.google.com/?q={data['lat']},{data['lon']}"
    admin_text += f"\nTovarlar: {len(cart)}"
    if data["delivery_price"] is not None:
        admin_text += f"\nSumma: {order['total']:,}".replace(",", " ")
    else:
        admin_text += "\n⚠️ Yetkazish narxi belgilanishi kerak (boshqa hudud)"

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception:
            pass

    await callback.answer()


@router.callback_query(Checkout.confirm, F.data == "order_cancel")
async def checkout_cancel(callback: CallbackQuery, state: FSMContext):
    lang = await _lang(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(t("btn_cancel", lang))
    await callback.message.answer(t("main_menu_client", lang), reply_markup=main_menu_kb(lang))
    await callback.answer()
