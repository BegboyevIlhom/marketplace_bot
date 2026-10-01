from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.admin_kb import admin_menu_kb_for_role, ADMIN_BTN_EXIT
from keyboards.client_kb import main_menu_kb
import db.database as db

router = Router()


def is_admin(tg_id: int) -> bool:
    """Faqat ADMIN_IDS (asosiy, to'liq huquqli admin)."""
    return tg_id in ADMIN_IDS


async def get_role(tg_id: int) -> str:
    """Foydalanuvchining admin-panel roli: 'admin' | 'manager' | 'courier' | '' (xodim emas)."""
    if is_admin(tg_id):
        return "admin"
    role = await db.get_staff_role(tg_id)
    return role or ""


async def can_manage_products(tg_id: int) -> bool:
    return await get_role(tg_id) in ("admin", "manager")


async def can_manage_orders(tg_id: int) -> bool:
    return await get_role(tg_id) in ("admin", "manager", "courier")


@router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if not role:
        return  # xodim bo'lmagan foydalanuvchiga hech qanday javob berilmaydi
    await state.clear()
    await message.answer("🛠 Admin panel", reply_markup=admin_menu_kb_for_role(role))


@router.message(F.text == ADMIN_BTN_EXIT)
async def exit_admin_panel(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if not role:
        return
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"] or "ru"
    await message.answer("👤 Client menu", reply_markup=main_menu_kb(lang))
