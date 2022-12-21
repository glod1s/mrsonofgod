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
from aiogram.types import Message, BotCommand, input_file
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
            BotCommand("translate", "переклад слів (українська та англійська)")

        ]
    )


async def schedule():
    aioschedule.every().day.at("5:00").do(todoist_message)
    aioschedule.every().hour.do(check_groups)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def todoist_message():
    tasks = check_items_todoist()
    if tasks != 0:
        message = "📑Доброго ранку! Ваші цілі на сьогодні:\n" + tasks
        await bot.send_message(GOD, message, disable_web_page_preview=True)


async def check_groups():
    list_notfull = db.not_full_groups()
    await bot.send_message(-1001736023833, "🔵🔵🔵🔵🔵\nChecking left started\n🔵🔵🔵🔵🔵")
    for i in list_notfull:
        result = alilink(i[0])
        if result != 0 and result[2] != i[1]:
            try:
                info = db.get_textid(i[0])
                text = info[0]
                if result[2] == 0:
                    needpeoplenewtext = "✅ <b>Group is full! You can buy it!</b> ✅"
                elif result[2] == 1:
                    needpeoplenewtext = "⚠️ <b>Need 1 person</b> ⚠️"
                else:
                    needpeoplenewtext = f"⚠️ <b>Need {str(result[2])} people</b> ⚠️"

                if i[1] == 0:
                    needpeopleoldtext = "✅ <b>Group is full! You can buy it!</b> ✅"
                elif i[1] == 1:
                    needpeopleoldtext = "⚠️ <b>Need 1 person</b> ⚠️"
                else:
                    needpeopleoldtext = f"⚠️ <b>Need {str(i[1])} people</b> ⚠️"
                text = text.replace(needpeopleoldtext, needpeoplenewtext)
                db.update_left(result[2], text, i[0])
                await bot.send_message(-1001796338322, f'UPDATE|||||{info[1]}|||||{text}', parse_mode="Markdown")
            except Exception as e:
                await bot.send_message(-1001736023833, f"🔴🔴🔴🔴🔴\nTroubles with {i[0]}\n{e}\n🔴🔴🔴🔴🔴")
            finally:
                await asyncio.sleep(5)
        try:
            delete_ali_photo(result[1])
        except:
            pass
    await bot.send_message(-1001736023833, "🟢🟢🟢🟢🟢\nChecking left finished\n🟢🟢🟢🟢🟢")


@dp.message_handler(user_id=ALLOWED_USERS, commands=['start'])
async def start(message: Message):
    await message.answer('У повній готовності!')


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer('Працюю лише з обраними людьми.')


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

