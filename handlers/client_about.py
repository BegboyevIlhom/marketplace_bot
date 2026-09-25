from aiogram import Router, F
from aiogram.types import Message

import db.database as db
from utils.texts import t

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(F.text.in_(["ℹ️ О нас", "ℹ️ Biz haqimizda"]))
async def show_about(message: Message):
    lang = await _lang(message.from_user.id)
    shop_name = await db.get_setting("shop_name")
    about = await db.get_setting("about_ru" if lang == "ru" else "about_uz")
    address = await db.get_setting("address")
    work_hours = await db.get_setting("work_hours")
    contacts = await db.get_setting("contacts")

    if lang == "ru":
        text = (
            f"🏪 <b>{shop_name}</b>\n\n{about}\n\n"
            f"📍 Адрес: {address}\n🕒 График: {work_hours}\n📞 Контакты: {contacts}"
        )
    else:
        text = (
            f"🏪 <b>{shop_name}</b>\n\n{about}\n\n"
            f"📍 Manzil: {address}\n🕒 Ish vaqti: {work_hours}\n📞 Kontaktlar: {contacts}"
        )
    await message.answer(text, parse_mode="HTML")
