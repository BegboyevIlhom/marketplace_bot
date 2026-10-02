from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from handlers.admin_menu import is_admin
from utils.states import AddPromo
from keyboards.admin_kb import (
    promo_menu_kb, promo_type_kb, promo_skip_maxuses_kb, promo_list_kb,
)
from utils.admin_texts import all_variants

router = Router()


@router.message(F.text.in_(all_variants("btn_promo")))
async def promo_menu(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🎟 Promo-kodlar:", reply_markup=promo_menu_kb())


@router.callback_query(F.data == "promo_new")
async def promo_new_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer("Promo-kod matnini kiriting (masalan: SALE10):")
    await state.set_state(AddPromo.code)
    await callback.answer()


@router.message(AddPromo.code)
async def promo_code_entered(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    if not code or " " in code:
        await message.answer("Promo-kod bo'sh joysiz, bitta so'z bo'lishi kerak. Qayta kiriting:")
        return
    await state.update_data(promo_code=code)
    await message.answer("Chegirma turini tanlang:", reply_markup=promo_type_kb())
    await state.set_state(AddPromo.type)


@router.callback_query(AddPromo.type, F.data.startswith("promotype:"))
async def promo_type_chosen(callback: CallbackQuery, state: FSMContext):
    discount_type = callback.data.split(":")[1]
    await state.update_data(discount_type=discount_type)
    if discount_type == "percent":
        await callback.message.answer("Chegirma foizini kiriting (masalan 10):")
    else:
        await callback.message.answer("Chegirma summasini kiriting (so'mda):")
    await state.set_state(AddPromo.value)
    await callback.answer()


@router.message(AddPromo.value)
async def promo_value_entered(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam kiriting:")
        return
    await state.update_data(discount_value=int(message.text))
    await message.answer(
        "Promo-kod necha marta ishlatilishi mumkin? (raqam kiriting, yoki cheksiz uchun tugmani bosing):",
        reply_markup=promo_skip_maxuses_kb(),
    )
    await state.set_state(AddPromo.max_uses)


@router.callback_query(AddPromo.max_uses, F.data == "promo_skip_maxuses")
async def promo_skip_maxuses(callback: CallbackQuery, state: FSMContext):
    await _save_promo(callback.message, state, max_uses=None)
    await callback.answer()


@router.message(AddPromo.max_uses)
async def promo_maxuses_entered(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam kiriting, yoki tugmani bosing:")
        return
    await _save_promo(message, state, max_uses=int(message.text))


async def _save_promo(message: Message, state: FSMContext, max_uses: int | None):
    data = await state.get_data()
    await db.create_promo_code(
        data["promo_code"], data["discount_type"], data["discount_value"], max_uses
    )
    await state.clear()
    value = f"{data['discount_value']}%" if data["discount_type"] == "percent" else f"{data['discount_value']:,}".replace(",", " ")
    await message.answer(f"✅ Promo-kod yaratildi: {data['promo_code']} — {value}")


@router.callback_query(F.data == "promo_list")
async def promo_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    promos = await db.get_all_promo_codes()
    if not promos:
        await callback.answer("Promo-kodlar hali yo'q.", show_alert=True)
        return
    await callback.message.answer("📋 Promo-kodlar ro'yxati:", reply_markup=promo_list_kb(promos))
    await callback.answer()


@router.callback_query(F.data.startswith("promotoggle:"))
async def promo_toggle(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    code = callback.data.split(":", 1)[1]
    promo = await db.get_promo_code(code)
    if not promo:
        await callback.answer()
        return
    await db.toggle_promo_code(code, not promo["active"])
    promos = await db.get_all_promo_codes()
    await callback.message.edit_reply_markup(reply_markup=promo_list_kb(promos))
    await callback.answer("Holat o'zgartirildi ✅")
