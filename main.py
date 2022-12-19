import aiogram
import config
import asyncio
import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
loop = asyncio.get_event_loop()
bot = aiogram.Bot(config.BOT_TOKEN, parse_mode='HTML')
dp = aiogram.Dispatcher(bot, loop=loop, storage=storage)

if __name__ == '__main__':
    from handlers import dp, start_message_for_admin, schedule
    dp.loop.create_task(schedule())
    aiogram.executor.start_polling(dp, on_startup=start_message_for_admin)