import asyncio
import logging
import time

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, PORT
import db.database as db
from db.database import init_db

from handlers import (
    client_start, client_catalog, client_cart, client_checkout,
    client_orders, client_about, client_support, client_search, client_favorites, common,
    admin_menu, admin_products, admin_orders, admin_settings,
    admin_broadcast, admin_stats, admin_support, admin_search,
    admin_export, admin_promo, admin_staff,
)


async def health_check(request):
    """Render/Railway kabi platformalar shu manzilga so'rov yuborib,
    xizmat 'tirik' ekanini tekshiradi. Shuningdek, UptimeRobot kabi
    bepul monitoring xizmatlari orqali bepul tarifni uyg'oq saqlash uchun
    ham shu manzil ishlatiladi."""
    return web.Response(text="Bot ishlayapti ✅")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Health-check server {PORT}-portda ishga tushdi")


async def cart_reminder_loop(bot: Bot):
    """Savatida mahsulot qoldirib, buyurtma bermagan mijozlarga
    bir martalik eslatma yuboradi. Har 15 daqiqada tekshiradi."""
    from utils.texts import t
    from keyboards.client_kb import cart_reminder_kb

    while True:
        try:
            raw = await db.get_setting("cart_reminder_delay_hours")
            delay_hours = float(raw) if raw else 2.0
        except Exception:
            delay_hours = 2.0

        threshold = int(time.time()) - int(delay_hours * 3600)
        try:
            users = await db.get_users_needing_reminder(threshold)
            for user in users:
                lang = user["language"] or "ru"
                try:
                    await bot.send_message(
                        user["tg_id"], t("cart_reminder_text", lang), reply_markup=cart_reminder_kb(lang)
                    )
                    await db.mark_reminder_sent(user["id"])
                except Exception:
                    pass
        except Exception as e:
            logging.warning(f"cart_reminder_loop xatolik: {e}")

        await asyncio.sleep(900)  # 15 daqiqa


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    await start_web_server()

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin_menu.router)
    dp.include_router(admin_products.router)
    dp.include_router(admin_orders.router)
    dp.include_router(admin_settings.router)
    dp.include_router(admin_broadcast.router)
    dp.include_router(admin_stats.router)
    dp.include_router(admin_support.router)
    dp.include_router(admin_search.router)
    dp.include_router(admin_export.router)
    dp.include_router(admin_promo.router)
    dp.include_router(admin_staff.router)

    dp.include_router(client_start.router)
    dp.include_router(client_catalog.router)
    dp.include_router(client_search.router)
    dp.include_router(client_favorites.router)
    dp.include_router(client_cart.router)
    dp.include_router(client_checkout.router)
    dp.include_router(client_orders.router)
    dp.include_router(client_about.router)
    dp.include_router(client_support.router)
    dp.include_router(common.router)

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(cart_reminder_loop(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
