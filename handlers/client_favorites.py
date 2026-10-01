from aiogram import Router, F
from aiogram.types import Message

import db.database as db
from utils.texts import t
from keyboards.client_kb import search_results_kb

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(F.text.in_(["❤️ Избранное", "❤️ Sevimlilar"]))
async def show_favorites(message: Message):
    lang = await _lang(message.from_user.id)
    user = await db.get_or_create_user(message.from_user.id)
    favs = await db.get_favorites(user["id"])
    if not favs:
        await message.answer(t("favorites_empty", lang))
        return
    await message.answer(t("favorites_title", lang), reply_markup=search_results_kb(favs, lang))
