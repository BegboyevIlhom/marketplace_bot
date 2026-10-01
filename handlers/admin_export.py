import csv
import io
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile

import db.database as db
from handlers.admin_menu import can_manage_products
from keyboards.admin_kb import ADMIN_BTN_EXPORT

router = Router()


@router.message(F.text == ADMIN_BTN_EXPORT)
async def export_customers(message: Message):
    if not await can_manage_products(message.from_user.id):
        return
    users = await db.get_all_users()
    if not users:
        await message.answer("Mijozlar hali yo'q.")
        return

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Telegram ID", "Ism", "Telefon", "Til", "Ro'yxatdan o'tgan sana"])
    for u in users:
        date_str = (
            datetime.fromtimestamp(u["created_at"]).strftime("%Y-%m-%d %H:%M")
            if u["created_at"] else "-"
        )
        writer.writerow([u["id"], u["tg_id"], u["name"] or "-", u["phone"] or "-", u["language"] or "-", date_str])

    # utf-8-sig: Excel'da ochganda o'zbek/rus harflari to'g'ri ko'rinishi uchun BOM qo'shiladi
    data = buf.getvalue().encode("utf-8-sig")
    filename = f"mijozlar_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    file = BufferedInputFile(data, filename=filename)
    await message.answer_document(file, caption=f"📥 Jami mijozlar: {len(users)}")
