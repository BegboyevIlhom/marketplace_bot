from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

import db.database as db
from utils.texts import t, status_text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.client_kb import orders_tabs_kb
from config import ADMIN_IDS

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


def _order_line(order: dict, lang: str) -> str:
    total = f"{order['total']:,}".replace(",", " ") if order["total"] else "-"
    pay = "✅" if order["payment_status"] == "paid" else "🕓"
    return f"№{order['id']} | {status_text(order['status'], lang)} | {pay} | {total}"


def _reorder_kb(orders: list[dict], lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{t('reorder_btn', lang)} №{o['id']}", callback_data=f"reorder:{o['id']}")]
        for o in orders
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(F.text.in_(["📦 Заказы", "📦 Buyurtmalar"]))
async def show_orders_menu(message: Message):
    lang = await _lang(message.from_user.id)
    await message.answer(t("btn_orders", lang), reply_markup=orders_tabs_kb(lang))


@router.callback_query(F.data.startswith("orders:"))
async def show_orders_list(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    active = callback.data.split(":")[1] == "active"
    user = await db.get_or_create_user(callback.from_user.id)
    orders = await db.get_user_orders(user["id"], active)
    if not orders:
        await callback.message.edit_text(t("no_orders", lang))
        await callback.answer()
        return
    text = "\n".join(_order_line(o, lang) for o in orders)
    await callback.message.edit_text(text)
    if orders:
        await callback.message.answer("🔁", reply_markup=_reorder_kb(orders, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("reorder:"))
async def reorder(callback: CallbackQuery):
    lang = await _lang(callback.from_user.id)
    order_id = int(callback.data.split(":")[1])
    user = await db.get_or_create_user(callback.from_user.id)
    order = await db.get_order(order_id)

    if not order or order["user_id"] != user["id"]:
        await callback.answer()
        return

    items = await db.get_order_items(order_id)
    added, skipped = 0, 0
    for item in items:
        if not item["product_id"]:
            skipped += 1
            continue
        p = await db.get_product(item["product_id"])
        if not p or p["is_deleted"] or p["is_hidden"] or not p["available"]:
            skipped += 1
            continue
        await db.add_to_cart(user["id"], item["product_id"], item["quantity"])
        added += 1

    await callback.message.answer(t("reorder_done", lang, added=added, skipped=skipped))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_receipt:"))
async def confirm_receipt(callback: CallbackQuery, bot: Bot):
    lang = await _lang(callback.from_user.id)
    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)
    user = await db.get_or_create_user(callback.from_user.id)

    # Faqat aynan shu buyurtmaning egasi tasdiqlashi mumkin
    if not order or order["user_id"] != user["id"]:
        await callback.answer()
        return

    if order["status"] != "shipped":
        # Allaqachon tasdiqlangan yoki boshqa holatda - qayta ishlov berilmaydi
        await callback.answer(t("receipt_confirmed_client", lang))
        return

    await db.update_order_status(order_id, "received")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer(t("receipt_confirmed_client", lang), show_alert=True)

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id, f"📥 Mijoz buyurtmani qabul qildi — №{order_id}. Endi \"Yakunlash\" tugmasi mavjud."
            )
        except Exception:
            pass
