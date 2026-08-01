import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database.engine import init_db
from bot.handlers import build_root_router
from bot.middlewares.activity import ActivityMiddleware
from bot.middlewares.db_session import DbSessionMiddleware
from bot.middlewares.user_context import UserContextMiddleware
from bot.services.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db()
    try:
        from scripts.seed_demo_data import seed

        await seed()
    except Exception:
        logger.warning("Demo data seeding skipped", exc_info=True)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.outer_middleware(UserContextMiddleware())
    dp.update.outer_middleware(ActivityMiddleware())

    dp.include_router(build_root_router())

    me = await bot.get_me()
    dp["bot_username"] = me.username
    logger.info("Starting bot @%s", me.username)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
