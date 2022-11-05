import asyncio
import aioschedule

import translation
from db import SQ

from alimain import alilink, delete_ali_photo
from todoist_check import check_items_todoist
from aiogram.dispatcher import FSMContext
from states import *
from main import bot, dp
from aiogram.utils import exceptions
from aiogram.types import Message, BotCommand, input_file, InputMediaPhoto
from aiogram.types.message import ContentType
from config import GOD, ALLOWED_USERS

db = SQ('/home/ubuntu/bots/db/db.db')

async def start_message_for_admin(dp):
    try:
        await bot.send_message(GOD, 'Татку, я живий!')
    except exceptions.BotBlocked:
        pass
    await dp.bot.set_my_commands(
        [
            BotCommand("start", "працездатність"),
            BotCommand("translate", "переклад слів (українська та англійська)"),
            BotCommand("noref", "посилання без рефералки"),
            BotCommand("aligroupbuy", "отримати готовий пост для AliGroupBuy")

        ]
    )


async def schedule():
    aioschedule.every().day.at("5:00").do(todoist_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def todoist_message():
    tasks = check_items_todoist()
    if tasks != 0:
        message = "📑Доброго ранку! Ваші цілі на сьогодні:\n" + tasks
        await bot.send_message(GOD, message, disable_web_page_preview=True)


@dp.message_handler(user_id=ALLOWED_USERS, commands=['start'])
async def start(message: Message):
    await message.answer('У повній готовності!')


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer('Працюю лише з обраними людьми.')


@dp.message_handler(user_id=ALLOWED_USERS, commands=['aligroupbuy'])
async def ali(message: Message):
    await message.answer('Надішліть посилання на свою групу')
    await AliLink.waitingLink.set()


@dp.message_handler(user_id=ALLOWED_USERS, commands=['noref'])
async def noref(message: Message):
    norefs = db.get_noref()
    text = ""
    for i in norefs:
        text += f"{i[0]}\n"
    try:
        await message.answer(text)
    except:
        await message.answer("Something went wrong. Probably message is too big")


@dp.message_handler(user_id=ALLOWED_USERS, commands=['translate'], state=None)
async def translate(message: Message):
    await message.answer('🔤Введіть слово, яке хочете перекласти, або /cancel')
    await Translation.translate.set()


@dp.message_handler(commands=['cancel'], state=[AliLink.waitingLink, Translation.translate])
async def cancel_translation(message: Message, state=FSMContext):
    await state.finish()
    await message.answer('Cancelled')


@dp.message_handler(state=AliLink.waitingLink)
async def ali_send(message: Message, state=FSMContext):
    await state.finish()
    msg = await message.answer('Please, wait')
    result = alilink(message.text)
    await message.answer_photo(input_file.InputFile(result[1]), result[0])
    delete_ali_photo(result[1])
    await msg.delete()


@dp.message_handler(state=Translation.translate)
async def translate_send(message: Message, state=FSMContext):
    word = message.text
    await state.finish()
    await message.answer(translation.parse(word), disable_web_page_preview=True)


@dp.message_handler(user_id=ALLOWED_USERS, content_types=ContentType.ANY)
async def parse_groups(message: Message):
    string = message.text
    if string is None:
        string = message.caption
    word = "https://a.aliexpress.com/_"
    word1 = "https://s.click.aliexpress.com/e/_"
    if word in string and word1 in string:
        links = string.strip().split(" ")
        oldlink = links[0]
        newlink = links[1]
        if not db.check_noref(oldlink):
            info = db.get_textid(oldlink)
            text = info[0].replace(oldlink, newlink)
            await bot.edit_message_caption("@aligroupbuychannel", info[1], caption=text)
            db.update(text, oldlink)
    elif word in string or word1 in string:
        if word1 in string:
            start = string.find(word1)
            link = string[start:start + 41]
        else:
            start = string.find(word)
            link = string[start:start + 33]
        msg = await message.answer('Please, wait')
        result = alilink(link)
        await message.answer_photo(input_file.InputFile(result[1]), result[0])
        if db.link_exists(link):
            info = db.get_textid(link)
            await bot.edit_message_media(InputMediaPhoto(open(result[1], 'rb'), caption=info[0]), chat_id="@aligroupbuychannel", message_id=info[1])
        delete_ali_photo(result[1])
        await msg.delete()

