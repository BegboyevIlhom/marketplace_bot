from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from db.database import SETTINGS_LABELS
from handlers.admin_menu import is_admin
from utils.states import SettingEdit
from keyboards.admin_kb import settings_kb, ADMIN_BTN_SETTINGS

router = Router()


@router.message(F.text == ADMIN_BTN_SETTINGS)
async def show_settings(message: Message):
    if not is_admin(message.from_user.id):
        return
    settings = await db.get_all_settings()
    lines = ["⚙️ Joriy sozlamalar:\n"]
    for key, label in SETTINGS_LABELS.items():
        value = settings.get(key, "-")
        short = value if len(value) < 60 else value[:57] + "..."
        lines.append(f"{label['uz']}: {short}")
    await message.answer("\n".join(lines), reply_markup=settings_kb())


@router.callback_query(F.data.startswith("setkey:"))
async def choose_setting_key(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    await state.update_data(setting_key=key)
    await state.set_state(SettingEdit.waiting_value)
    label = SETTINGS_LABELS.get(key, {"uz": key})["uz"]
    current = await db.get_setting(key)
    await callback.message.answer(f"{label}\nHozirgi qiymat: {current}\n\nYangi qiymatni kiriting:")
    await callback.answer()


@router.message(SettingEdit.waiting_value)
async def save_setting_value(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data["setting_key"]
    await db.set_setting(key, message.text)
    await state.clear()
    await message.answer("✅ Sozlama yangilandi")
