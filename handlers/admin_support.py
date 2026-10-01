from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from handlers.admin_menu import can_manage_products
from utils.states import SupportReply
from utils.texts import t
from keyboards.client_kb import main_menu_kb

router = Router()


@router.callback_query(F.data.startswith("supreply:"))
async def support_reply_start(callback: CallbackQuery, state: FSMContext):
    if not await can_manage_products(callback.from_user.id):
        return
    _, msg_id, client_tg_id = callback.data.split(":")
    await state.update_data(reply_client_tg_id=int(client_tg_id))
    await state.set_state(SupportReply.waiting_reply)
    await callback.message.answer("Javob matnini kiriting:")
    await callback.answer()


@router.message(SupportReply.waiting_reply)
async def support_reply_send(message: Message, state: FSMContext, bot: Bot):
    if not await can_manage_products(message.from_user.id):
        return
    data = await state.get_data()
    client_tg_id = data["reply_client_tg_id"]
    await state.clear()

    user = await db.get_user(client_tg_id)
    lang = user["language"] if user and user["language"] else "ru"

    try:
        await bot.send_message(client_tg_id, t("support_reply_sent_to_client", lang, text=message.text))
        await message.answer(t("support_reply_confirmed", "ru"))
    except Exception:
        await message.answer("❌ Xabarni yuborib bo'lmadi (mijoz botni bloklagan bo'lishi mumkin)")
