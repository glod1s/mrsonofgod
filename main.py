import logging
import asyncio
from datetime import datetime, timedelta
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, BotCommand
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import exceptions
from aiogram.types.message import ContentType
from db import SQ
import aioschedule

db = SQ('/home/ubuntu/bots/db/db.db')

API_TOKEN = '5630951850:AAFVtJ6ik2taG2YDqYNbWsOmaPYtGB28BpM'

# Configure logging
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
loop = asyncio.get_event_loop()

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, loop=loop, storage=storage)

GOD = 512532936


async def schedule():
    aioschedule.every(5).minutes.do(clean_db)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def clean_db():
    items = db.get_old()
    db.clear()
    db.del_old_dailyslash()
    for i in items:
        if i[0] is not None:
            try:
                await bot.delete_message(-1001479987896, i[0])
            except:
                pass
        else:
            pass


async def start_message_for_admin(dp):
    try:
        await bot.send_message(GOD, 'Татку, я живий!')
    except exceptions.BotBlocked:
        pass


@dp.message_handler(user_id=GOD, commands=['db'])
async def database(message: types.Message):
    with open('/home/ubuntu/bots/db/db.db', 'rb') as a:
        await bot.send_document(message.from_user.id, a)


@dp.message_handler(user_id=GOD, commands=['cldb'])
async def cleardatabase(message: types.Message):
    db.clear_all()
    await message.reply('Done. Data base was cleared!')


@dp.message_handler(user_id=GOD, commands=['ref'])
async def noref(message: Message):
    norefs = db.get_noref()
    text = ""
    for i in norefs:
        text += f"{i[0]}\n"
    try:
        await message.answer(text)
    except:
        await message.answer("Something went wrong. Probably message is too big")


@dp.message_handler(user_id=GOD, content_types=ContentType.ANY)
async def god_chat(message: types.Message):
    string = message.text
    if string is None:
        string = message.caption
    word = "https://a.aliexpress.com/_"
    word1 = "https://s.click.aliexpress.com/e/_"
    if "Top On Sale Product Recommendations!" in string:
        try:
            text_split = string.split("\n")
            try:
                photo_id = message.photo[-1].file_id
                if "Available Code" in string:
                    coupun = text_split[6].split(' ')
                    coupountext = f"{coupun[0]} {coupun[1]} <b><code>{coupun[2].replace(',', '')}</code>, USD {coupun[3].replace('USD', '')} off</b>"
                    text = f"♨️ #HotDeals ♨️\nℹ️ {text_split[1]} ℹ️\n\n" \
                           f"📛 Original price: <s>{text_split[2].replace('Original price: ', '')}</s> 📛\n" \
                           f"🤑 <b>{text_split[3]}</b> 🤑\n" \
                           f"😱 {coupountext} 😱\n\n" \
                           f"🔥 {text_split[8].replace('Click&Buy:', '')} 🔥\n\n" \
                           f"❤️‍🔥 <i><a href='https://t.me/aliforum'>Find more products here!</a></i> ❤️‍🔥"
                else:
                    text = f"♨️ #HotDeals ♨️\nℹ️ {text_split[1]} ℹ️\n\n" \
                           f"📛 Original price: <s>{text_split[2].replace('Original price: ', '')}</s> 📛\n" \
                           f"🤑 <b>{text_split[3]}</b> 🤑\n\n" \
                           f"🔥 {text_split[7].replace('Click&Buy:', '')} 🔥\n\n" \
                           f"❤️‍🔥 <i><a href='https://t.me/aliforum'>Find more products here!</a></i> ❤️‍🔥"
                await message.answer_photo(photo_id, text)
                await bot.send_photo("@aliforum", photo_id, text, message_thread_id=1597)
            except:
                await message.answer("Something wrong with photo")
        except:
            await message.answer("Something wrong with text")

    if word in string and word1 in string:
        oldstart = string.find(word)
        newstart = string.find(word1)
        oldlink = string[oldstart:oldstart + 33]
        newlink = string[newstart:newstart + 41]
        if db.check_noref(oldlink)[0] == 0:
            await bot.send_message(-1001796338322,
                                   f'{oldlink} {newlink}')
            await message.answer(f"Old link {oldlink} changed with {newlink} ✅")
            return 0


@dp.message_handler(chat_type=[types.ChatType.PRIVATE], content_types=ContentType.ANY)
async def echo(message: types.Message):
    await message.answer('HELLO!\n\nIf you want to send your Group Buy, check our new forum and the topic "GROUP BUY"\n'
                         'Link: https://t.me/aliforum')


@dp.message_handler(chat_id=-1001479987896, content_types=ContentType.ANY)
async def admin_chat(message: Message):
    # del messages join or left members
    try:
        if message.left_chat_member or message.new_chat_members:
            await message.delete()
    except:
        pass

    # GB link recognition in GB topic
    if message.message_thread_id == 1586:
        string = message.text
        if string is None:
            string = message.caption
        word = "https://a.aliexpress.com/_"
        if word in string:
            if "GoGo Match" not in string:
                start = string.find(word)
                link = string[start:start + 33]
                if not db.link_exists(link):
                    db.add_link(link, message.from_user.id)
                    await bot.send_message(-1001796338322,
                                           f'{link}\n⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️\n<a href="tg://user?id={message.from_user.id}">user</a> from group chat')
            await message.delete()
        else:
            if message.from_id != -1001479987896:
                await message.delete()

    # del messages in private topics
    if message.message_thread_id == 1589 or message.message_thread_id == 1597 or message.message_thread_id == 1590:
        if message.from_id != -1001479987896:
            await message.delete()



@dp.message_handler(chat_type=[types.ChatType.GROUP, types.ChatType.SUPER_GROUP, types.ChatType.SUPERGROUP],
                    content_types=ContentType.ANY)
async def parse_groups(message: Message):
    if message.chat.id != -1001796338322:
        string = message.text
        if string is None:
            string = message.caption
        word = "https://a.aliexpress.com/_"
        if word in string:
            if "GoGo Match" not in string:
                start = string.find(word)
                link = string[start:start + 33]
                if not db.link_exists(link):
                    db.add_link(link, message.from_user.id)
                    await bot.send_message(-1001796338322,
                                           f'{link}\n⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️\n<a href="tg://user?id={message.from_user.id}">user</a> from group chat')


if __name__ == '__main__':
    dp.loop.create_task(schedule())
    executor.start_polling(dp, on_startup=start_message_for_admin)
