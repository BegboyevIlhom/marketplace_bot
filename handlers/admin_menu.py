from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.admin_kb import admin_main_menu_kb, ADMIN_BTN_EXIT
from keyboards.client_kb import main_menu_kb
import db.database as db

router = Router()


def is_admin(tg_id: int) -> bool:
    return tg_id in ADMIN_IDS


@router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return  # oddiy foydalanuvchiga hech qanday javob berilmaydi - admin ekanini bilmasin
    await state.clear()
    await message.answer("🛠 Admin panel", reply_markup=admin_main_menu_kb())


@router.message(F.text == ADMIN_BTN_EXIT)
async def exit_admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"] or "ru"
    await message.answer("👤 Client menu", reply_markup=main_menu_kb(lang))
