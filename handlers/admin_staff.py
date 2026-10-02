from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from handlers.admin_menu import is_admin
from utils.states import AddStaff
from keyboards.admin_kb import staff_list_kb, staff_role_kb
from utils.admin_texts import all_variants

router = Router()

ROLE_NAMES = {"manager": "Sotuvchi", "courier": "Kuryer"}


@router.message(F.text.in_(all_variants("btn_staff")))
async def staff_menu(message: Message):
    if not is_admin(message.from_user.id):
        return
    staff = await db.get_all_staff()
    if staff:
        lines = ["👥 Xodimlar:\n"]
        for s in staff:
            lines.append(f"{s['tg_id']} — {ROLE_NAMES.get(s['role'], s['role'])}")
        text = "\n".join(lines)
    else:
        text = "Xodimlar hali yo'q."
    await message.answer(text, reply_markup=staff_list_kb(staff))


@router.callback_query(F.data == "staff_add")
async def staff_add_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.answer(
        "Yangi xodimning Telegram ID raqamini kiriting "
        "(xodim avval botga /start yuborib, @userinfobot orqali o'z ID'sini olishi mumkin):"
    )
    await state.set_state(AddStaff.tg_id)
    await callback.answer()


@router.message(AddStaff.tg_id)
async def staff_add_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam (Telegram ID) kiriting:")
        return
    await state.update_data(new_staff_id=int(message.text))
    await message.answer("Rolini tanlang:", reply_markup=staff_role_kb())
    await state.set_state(AddStaff.role)


@router.callback_query(AddStaff.role, F.data.startswith("staffrole:"))
async def staff_add_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":")[1]
    data = await state.get_data()
    await db.add_staff(data["new_staff_id"], role)
    await state.clear()
    await callback.message.answer(
        f"✅ Xodim qo'shildi: {data['new_staff_id']} — {ROLE_NAMES.get(role, role)}\n"
        f"Endi u o'z Telegram'ida /admin buyrug'ini yuborib panelga kira oladi."
    )
    await callback.answer()


@router.callback_query(F.data.startswith("staffdel:"))
async def staff_remove(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    tg_id = int(callback.data.split(":")[1])
    await db.remove_staff(tg_id)
    staff = await db.get_all_staff()
    await callback.message.edit_reply_markup(reply_markup=staff_list_kb(staff))
    await callback.answer("O'chirildi ✅")
