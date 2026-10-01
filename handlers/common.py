from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    """Faqat ma'lumot ko'rsatuvchi (bosilmaydigan) tugmalar uchun -
    Telegram'da cheksiz 'yuklanmoqda' holatida qolib ketmasligi uchun."""
    await callback.answer()
