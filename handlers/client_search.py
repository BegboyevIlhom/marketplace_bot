from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import db.database as db
from utils.states import Search
from utils.texts import t
from keyboards.client_kb import search_results_kb

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(F.text.in_(["🔍 Поиск", "🔍 Qidiruv"]))
async def start_search(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    await message.answer(t("search_ask", lang))
    await state.set_state(Search.waiting_query)


@router.message(Search.waiting_query)
async def run_search(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    await state.clear()
    query = message.text.strip()
    products = await db.search_products(query)
    if not products:
        await message.answer(t("search_no_results", lang))
        return
    await message.answer(t("search_results_title", lang), reply_markup=search_results_kb(products, lang))
