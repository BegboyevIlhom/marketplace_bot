from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from db.database import SETTINGS_LABELS
from handlers.admin_menu import is_admin, _admin_lang
from utils.states import SettingEdit
from keyboards.admin_kb import settings_kb
from utils.admin_texts import all_variants

router = Router()


@router.message(F.text.in_(all_variants("btn_settings")))
async def show_settings(message: Message):
    if not is_admin(message.from_user.id):
        return
    lang = await _admin_lang(message.from_user.id)
    settings = await db.get_all_settings()
    title = "⚙️ Текущие настройки:\n" if lang == "ru" else "⚙️ Joriy sozlamalar:\n"
    lines = [title]
    for key, label in SETTINGS_LABELS.items():
        value = settings.get(key, "-")
        short = value if len(value) < 60 else value[:57] + "..."
        lines.append(f"{label[lang]}: {short}")
    await message.answer("\n".join(lines), reply_markup=settings_kb(lang))


@router.callback_query(F.data.startswith("setkey:"))
async def choose_setting_key(callback: CallbackQuery, state: FSMContext):
    lang = await _admin_lang(callback.from_user.id)
    key = callback.data.split(":")[1]
    await state.update_data(setting_key=key)
    await state.set_state(SettingEdit.waiting_value)
    label = SETTINGS_LABELS.get(key, {lang: key})[lang]
    current = await db.get_setting(key)
    if lang == "ru":
        text = f"{label}\nТекущее значение: {current}\n\nВведите новое значение:"
    else:
        text = f"{label}\nHozirgi qiymat: {current}\n\nYangi qiymatni kiriting:"
    await callback.message.answer(text)
    await callback.answer()


@router.message(SettingEdit.waiting_value)
async def save_setting_value(message: Message, state: FSMContext):
    lang = await _admin_lang(message.from_user.id)
    data = await state.get_data()
    key = data["setting_key"]
    await db.set_setting(key, message.text)
    await state.clear()
    await message.answer("✅ Настройка обновлена" if lang == "ru" else "✅ Sozlama yangilandi")
