from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import db.database as db
from utils.states import Support
from utils.texts import t
from keyboards.client_kb import main_menu_kb
from keyboards.admin_kb import support_reply_kb
from config import ADMIN_IDS

router = Router()


async def _lang(tg_id: int) -> str:
    user = await db.get_user(tg_id)
    return user["language"] if user and user["language"] else "ru"


@router.message(F.text.in_(["💬 Связаться с админом", "💬 Admin bilan bog'lanish"]))
async def ask_support_question(message: Message, state: FSMContext):
    lang = await _lang(message.from_user.id)
    await message.answer(t("support_ask_question", lang))
    await state.set_state(Support.waiting_message)


@router.message(Support.waiting_message)
async def receive_support_question(message: Message, state: FSMContext, bot: Bot):
    lang = await _lang(message.from_user.id)
    user = await db.get_or_create_user(message.from_user.id)
    msg_id = await db.add_support_message(user["id"], message.text)
    await state.clear()
    await message.answer(t("support_sent", lang), reply_markup=main_menu_kb(lang))

    admin_text = t(
        "support_admin_notify", "ru",
        name=user["name"] or "-", phone=user["phone"] or "-", text=message.text,
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id, admin_text, reply_markup=support_reply_kb(msg_id, message.from_user.id)
            )
        except Exception:
            pass
