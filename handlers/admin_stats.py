import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import db.database as db
from handlers.admin_menu import is_admin
from keyboards.admin_kb import stats_period_kb
from utils.admin_texts import all_variants

router = Router()


@router.message(F.text.in_(all_variants("btn_stats")))
async def show_stats_menu(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Davrni tanlang:", reply_markup=stats_period_kb())


@router.callback_query(F.data.startswith("stats:"))
async def show_stats(callback: CallbackQuery):
    days = int(callback.data.split(":")[1])
    since_ts = int(time.time()) - days * 86400
    stats = await db.get_sales_stats(since_ts)

    lines = [
        f"📊 So'nggi {days} kun statistikasi:\n",
        f"Buyurtmalar soni: {stats['total_orders']}",
        f"To'langan buyurtmalar: {stats['paid_orders']}",
        f"Tushum: {stats['revenue']:,}".replace(",", " "),
        f"O'rtacha chek: {stats['avg_check']:,}".replace(",", " "),
        "",
        "TOP mahsulotlar:",
    ]
    if stats["top_products"]:
        for p in stats["top_products"]:
            lines.append(f"• {p['name_ru']}: {p['qty']} dona / {p['revenue']:,}".replace(",", " "))
    else:
        lines.append("Ma'lumot yo'q")

    await callback.message.edit_text("\n".join(lines))
    await callback.answer()
