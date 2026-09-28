import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, PORT
from db.database import init_db

from handlers import (
    client_start, client_catalog, client_cart, client_checkout,
    client_orders, client_about, client_support,
    admin_menu, admin_products, admin_orders, admin_settings,
    admin_broadcast, admin_stats, admin_support, admin_search,
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

    dp.include_router(client_start.router)
    dp.include_router(client_catalog.router)
    dp.include_router(client_cart.router)
    dp.include_router(client_checkout.router)
    dp.include_router(client_orders.router)
    dp.include_router(client_about.router)
    dp.include_router(client_support.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
