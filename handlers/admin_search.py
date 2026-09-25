from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import db.database as db
from handlers.admin_menu import is_admin
from utils.states import OrderSearch
from utils.texts import status_text

router = Router()


@router.message(Command("search"))
async def search_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(OrderSearch.waiting_query)
    await message.answer("Buyurtma raqami, telefon yoki ismni kiriting:")


@router.message(OrderSearch.waiting_query)
async def search_run(message: Message, state: FSMContext):
    await state.clear()
    orders = await db.search_orders(message.text.strip())
    if not orders:
        await message.answer("Hech narsa topilmadi.")
        return
    lines = []
    for o in orders:
        total = f"{o['total']:,}".replace(",", " ") if o["total"] else "-"
        lines.append(f"№{o['id']} | {o['recipient_name']} | {o['recipient_phone']} | {status_text(o['status'], 'ru')} | {total}")
    await message.answer("\n".join(lines))
