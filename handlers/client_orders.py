from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import db.database as db
from utils.texts import t, status_text
from keyboards.client_kb import orders_tabs_kb

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


def _order_line(order: dict, lang: str) -> str:
    total = f"{order['total']:,}".replace(",", " ") if order["total"] else "-"
    pay = "✅" if order["payment_status"] == "paid" else "🕓"
    return f"№{order['id']} | {status_text(order['status'], lang)} | {pay} | {total}"


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
    await callback.answer()
