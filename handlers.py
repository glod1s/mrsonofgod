import asyncio
import aioschedule

import translation

from alimain import alilink
from todoist_check import check_items_todoist
from aiogram.dispatcher import FSMContext
from states import *
from main import bot, dp
from aiogram.utils import exceptions
from aiogram.types import Message, BotCommand, input_file
from aiogram.types.message import ContentType
from config import GOD, ALLOWED_USERS


async def start_message_for_admin(dp):
    try:
        await bot.send_message(GOD, 'Татку, я живий!')
    except exceptions.BotBlocked:
        pass
    await dp.bot.set_my_commands(
        [
            BotCommand("start", "працездатність"),
            BotCommand("translate", "переклад слів (українська та англійська)"),
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
    text = alilink(message.text)
    await message.answer_photo(input_file.InputFile("pipka.png"), text)
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
    if word in string:
        start = string.find(word)
        link = string[start:start + 33]
        msg = await message.answer('Please, wait')
        text = alilink(link)
        await message.answer_photo(input_file.InputFile("pipka.png"), text)
        await msg.delete()
