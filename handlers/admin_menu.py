from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.admin_kb import admin_menu_kb_for_role
from keyboards.client_kb import main_menu_kb
from utils.admin_texts import at, all_variants
from utils.states import PinAuth, SetPin
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


async def _admin_lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if not role:
        return  # xodim bo'lmagan foydalanuvchiga hech qanday javob berilmaydi
    pin = await db.get_admin_pin(message.from_user.id)
    if pin:
        lang = await _admin_lang(message.from_user.id)
        await state.set_state(PinAuth.waiting_pin)
        await message.answer(at("pin_ask", lang))
        return
    await state.clear()
    lang = await _admin_lang(message.from_user.id)
    await message.answer("🛠 Admin panel", reply_markup=admin_menu_kb_for_role(role, lang))


@router.message(PinAuth.waiting_pin)
async def check_pin(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    lang = await _admin_lang(message.from_user.id)
    if not role:
        await state.clear()
        return
    pin = await db.get_admin_pin(message.from_user.id)
    if message.text and message.text.strip() == pin:
        await state.clear()
        await message.answer(at("pin_ok", lang), reply_markup=admin_menu_kb_for_role(role, lang))
    else:
        await message.answer(at("pin_wrong", lang))


@router.message(F.text.in_(all_variants("btn_exit")))
async def exit_admin_panel(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if not role:
        return
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)
    lang = user["language"] or "ru"
    await message.answer("👤", reply_markup=main_menu_kb(lang))


@router.message(F.text.in_(all_variants("btn_mystats")))
async def show_my_stats(message: Message):
    role = await get_role(message.from_user.id)
    if not role:
        return
    lang = await _admin_lang(message.from_user.id)
    stats = await db.get_staff_stats(message.from_user.id)
    text = (
        f"{at('mystats_title', lang)}\n\n"
        f"{at('mystats_products', lang)}: {stats['products_added']}\n"
        f"{at('mystats_orders', lang)}: {stats['orders_completed']}"
    )
    await message.answer(text)


@router.message(F.text.in_(all_variants("btn_set_pin")))
async def set_pin_start(message: Message, state: FSMContext):
    role = await get_role(message.from_user.id)
    if not role:
        return
    lang = await _admin_lang(message.from_user.id)
    await message.answer(at("pin_set_ask_new", lang))
    await state.set_state(SetPin.waiting_new)


@router.message(SetPin.waiting_new)
async def set_pin_new(message: Message, state: FSMContext):
    lang = await _admin_lang(message.from_user.id)
    pin = (message.text or "").strip()
    if not (pin.isdigit() and len(pin) == 4):
        await message.answer(at("pin_set_wrong_format", lang))
        return
    await state.update_data(new_pin=pin)
    await message.answer(at("pin_set_ask_confirm", lang))
    await state.set_state(SetPin.waiting_confirm)


@router.message(SetPin.waiting_confirm)
async def set_pin_confirm(message: Message, state: FSMContext):
    lang = await _admin_lang(message.from_user.id)
    data = await state.get_data()
    if (message.text or "").strip() != data.get("new_pin"):
        await message.answer(at("pin_set_mismatch", lang))
        await state.set_state(SetPin.waiting_new)
        return
    await db.set_admin_pin(message.from_user.id, data["new_pin"])
    await state.clear()
    await message.answer(at("pin_set_done", lang))
