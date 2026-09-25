from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from utils.states import Registration
from utils.texts import t
from keyboards.client_kb import language_kb, phone_request_kb, main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_or_create_user(message.from_user.id)

    if not user["language"]:
        await message.answer(t("choose_language", "ru"), reply_markup=language_kb())
        return

    lang = user["language"]
    if not user["phone"]:
        await message.answer(t("ask_phone", lang), reply_markup=phone_request_kb(lang))
        await state.set_state(Registration.waiting_phone)
        return

    greeting = await db.get_setting("greeting_ru" if lang == "ru" else "greeting_uz")
    await message.answer(greeting, reply_markup=main_menu_kb(lang))


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await db.set_user_language(callback.from_user.id, lang)
    await callback.message.delete()

    user = await db.get_user(callback.from_user.id)
    if not user["phone"]:
        await callback.message.answer(t("ask_phone", lang), reply_markup=phone_request_kb(lang))
        await state.set_state(Registration.waiting_phone)
    else:
        greeting = await db.get_setting("greeting_ru" if lang == "ru" else "greeting_uz")
        await callback.message.answer(greeting, reply_markup=main_menu_kb(lang))
    await callback.answer()


@router.message(Registration.waiting_phone, F.contact)
async def got_contact(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] or "ru"
    phone = message.contact.phone_number
    name = message.from_user.first_name or ""
    await db.set_user_contact(message.from_user.id, phone, name)
    await state.clear()
    await message.answer(t("registered", lang))
    greeting = await db.get_setting("greeting_ru" if lang == "ru" else "greeting_uz")
    await message.answer(greeting, reply_markup=main_menu_kb(lang))


@router.message(Registration.waiting_phone)
async def waiting_phone_wrong_input(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user["language"] or "ru"
    await message.answer(t("ask_phone", lang), reply_markup=phone_request_kb(lang))
