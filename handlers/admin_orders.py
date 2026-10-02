from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from handlers.admin_menu import can_manage_orders
from utils.states import SetDeliveryPrice, OrderSearch
from utils.texts import status_text, t
from keyboards.admin_kb import order_actions_kb
from utils.admin_texts import all_variants
from keyboards.client_kb import confirm_receipt_kb

router = Router()


def _order_card_text(order: dict, items: list[dict]) -> str:
    lines = [
        f"📦 Buyurtma №{order['id']}",
        f"Qabul qiluvchi: {order['recipient_name']}",
        f"Telefon: {order['recipient_phone']}",
        f"Manzil: {order['address']}",
    ]
    if order["location_lat"]:
        lines.append(f"📍 https://maps.google.com/?q={order['location_lat']},{order['location_lon']}")
    if order["comment"]:
        lines.append(f"Izoh: {order['comment']}")
    lines.append("")
    lines.append("Tovarlar:")
    for it in items:
        lines.append(f"• {it['name_ru']} x{it['quantity']} = {it['price']*it['quantity']:,}".replace(",", " "))
    lines.append("")
    lines.append(f"Mahsulotlar summasi: {order['items_total']:,}".replace(",", " "))
    if order["delivery_price"] is not None:
        lines.append(f"Yetkazish: {order['delivery_price']:,}".replace(",", " "))
        lines.append(f"JAMI: {order['total']:,}".replace(",", " "))
    else:
        lines.append("Yetkazish narxi: hali belgilanmagan")
    lines.append(f"Status: {status_text(order['status'], 'ru')}")
    pay_label = "✅ to'landi" if order["payment_status"] == "paid" else "🕓 kutilmoqda"
    lines.append(f"To'lov: {pay_label}")
    return "\n".join(lines)


async def _send_order_card(message: Message, order: dict):
    items = await db.get_order_items(order["id"])
    await message.answer(_order_card_text(order, items), reply_markup=order_actions_kb(order))


@router.message(F.text.in_(all_variants("btn_active_orders")))
async def show_active_orders(message: Message):
    if not await can_manage_orders(message.from_user.id):
        return
    orders = await db.get_active_orders()
    if not orders:
        await message.answer("Aktual buyurtmalar yo'q.")
        return
    for o in orders:
        await _send_order_card(message, o)


@router.message(F.text.in_(all_variants("btn_history_orders")))
async def show_history_orders(message: Message):
    if not await can_manage_orders(message.from_user.id):
        return
    orders = await db.get_history_orders()
    if not orders:
        await message.answer("Eski buyurtmalar yo'q.")
        return
    lines = []
    for o in orders:
        total = f"{o['total']:,}".replace(",", " ") if o["total"] else "-"
        lines.append(f"№{o['id']} | {status_text(o['status'], 'ru')} | {total}")
    await message.answer("\n".join(lines))


@router.message(F.text.in_(all_variants("btn_paid")))
async def show_paid_orders(message: Message):
    if not await can_manage_orders(message.from_user.id):
        return
    active = await db.get_active_orders()
    history = await db.get_history_orders()
    paid = [o for o in (active + history) if o["payment_status"] == "paid"]
    if not paid:
        await message.answer("To'langan buyurtmalar yo'q.")
        return
    total_sum = sum(o["total"] or 0 for o in paid)
    lines = [f"№{o['id']} — {o['total']:,}".replace(",", " ") for o in paid]
    lines.append("")
    lines.append(f"Jami: {total_sum:,}".replace(",", " "))
    await message.answer("\n".join(lines))


@router.callback_query(F.data.startswith("setstatus:"))
async def set_status(callback: CallbackQuery, bot: Bot):
    _, order_id, new_status = callback.data.split(":")
    order_id = int(order_id)
    handled_by = callback.from_user.id if new_status == "completed" else None
    await db.update_order_status(order_id, new_status, handled_by=handled_by)
    order = await db.get_order(order_id)
    user = await db.get_user_by_internal_id(order["user_id"])

    if user:
        lang = user["language"] or "ru"
        kb = confirm_receipt_kb(order_id, lang) if new_status == "shipped" else None
        try:
            await bot.send_message(
                user["tg_id"],
                t("status_changed_notify", lang, order_id=order_id, status=status_text(new_status, lang)),
                reply_markup=kb,
            )
        except Exception:
            pass

    await callback.message.edit_reply_markup(reply_markup=order_actions_kb(order))
    await callback.answer("Status yangilandi ✅")


@router.callback_query(F.data.startswith("markpaid:"))
async def mark_paid(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    await db.mark_order_paid(order_id)
    order = await db.get_order(order_id)

    import aiosqlite
    from db.database import DB_PATH
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM users WHERE id=?", (order["user_id"],))
        row = await cur.fetchone()
        user = dict(row) if row else None

    if user:
        lang = user["language"] or "ru"
        try:
            await bot.send_message(user["tg_id"], t("paid_notify", lang, order_id=order_id))
        except Exception:
            pass

    await callback.message.edit_reply_markup(reply_markup=order_actions_kb(order))
    await callback.answer("To'landi deb belgilandi ✅")


@router.callback_query(F.data.startswith("setdeliv:"))
async def ask_delivery_price(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])
    await state.update_data(delivery_order_id=order_id)
    await state.set_state(SetDeliveryPrice.waiting_price)
    await callback.message.answer("Yetkazish narxini kiriting (so'mda, faqat raqam):")
    await callback.answer()


@router.message(SetDeliveryPrice.waiting_price)
async def set_delivery_price_value(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam kiriting:")
        return
    data = await state.get_data()
    order_id = data["delivery_order_id"]
    price = int(message.text)
    new_total = await db.set_delivery_price(order_id, price)
    await state.clear()

    order = await db.get_order(order_id)
    user = await db.get_user_by_internal_id(order["user_id"])

    if user:
        lang = user["language"] or "ru"
        payment_info = await db.get_setting("payment_info")
        notify_text = t(
            "delivery_price_set_notify", lang, order_id=order_id,
            price=f"{price:,}".replace(",", " "), total=f"{new_total:,}".replace(",", " "),
        ) + f"\n\n{payment_info}"
        try:
            await bot.send_message(user["tg_id"], notify_text)
        except Exception:
            pass

    await message.answer(f"✅ Yetkazish narxi belgilandi: {price:,}".replace(",", " "))
    await _send_order_card(message, order)
