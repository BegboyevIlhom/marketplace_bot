import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import db.database as db
from handlers.admin_menu import is_admin
from utils.states import Broadcast
from keyboards.admin_kb import broadcast_type_kb, broadcast_confirm_kb
from utils.admin_texts import all_variants
from config import BROADCAST_DELAY

router = Router()


@router.message(F.text.in_(all_variants("btn_broadcast")))
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(Broadcast.choose_type)
    await message.answer("Post turini tanlang:", reply_markup=broadcast_type_kb())


@router.callback_query(Broadcast.choose_type, F.data.startswith("bc:"))
async def broadcast_choose_type(callback: CallbackQuery, state: FSMContext):
    bc_type = callback.data.split(":")[1]
    await state.update_data(bc_type=bc_type)
    await state.set_state(Broadcast.waiting_content)
    if bc_type == "text":
        await callback.message.answer("Matnni yuboring:")
    elif bc_type == "photo":
        await callback.message.answer("Rasm + izoh (caption) sifatida yuboring:")
    else:
        await callback.message.answer("Video + izoh (caption) sifatida yuboring:")
    await callback.answer()


@router.message(Broadcast.waiting_content)
async def broadcast_receive_content(message: Message, state: FSMContext):
    data = await state.get_data()
    bc_type = data["bc_type"]

    if bc_type == "text":
        await state.update_data(bc_text=message.text)
        await message.answer(message.text)
    elif bc_type == "photo" and message.photo:
        await state.update_data(bc_file_id=message.photo[-1].file_id, bc_text=message.caption or "")
        await message.answer_photo(message.photo[-1].file_id, caption=message.caption or "")
    elif bc_type == "video" and message.video:
        await state.update_data(bc_file_id=message.video.file_id, bc_text=message.caption or "")
        await message.answer_video(message.video.file_id, caption=message.caption or "")
    else:
        await message.answer("Noto'g'ri format. Qaytadan yuboring.")
        return

    await state.set_state(Broadcast.confirm)
    await message.answer("Yuqoridagi ko'rinishda barchaga yuborilsinmi?", reply_markup=broadcast_confirm_kb())


@router.callback_query(Broadcast.confirm, F.data == "bc_send")
async def broadcast_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    bc_type = data["bc_type"]
    user_ids = await db.get_all_user_tg_ids()

    sent, failed = 0, 0
    for tg_id in user_ids:
        try:
            if bc_type == "text":
                await bot.send_message(tg_id, data["bc_text"])
            elif bc_type == "photo":
                await bot.send_photo(tg_id, data["bc_file_id"], caption=data.get("bc_text", ""))
            else:
                await bot.send_video(tg_id, data["bc_file_id"], caption=data.get("bc_text", ""))
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(BROADCAST_DELAY)

    await state.clear()
    await callback.message.answer(f"✅ Yuborildi: {sent} ta\n❌ Xato: {failed} ta")
    await callback.answer()


@router.callback_query(Broadcast.confirm, F.data == "bc_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Bekor qilindi")
    await callback.answer()
