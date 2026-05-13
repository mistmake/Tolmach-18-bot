import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import info, quiz, start, words


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(words.router)
    dp.include_router(quiz.router)
    dp.include_router(info.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
