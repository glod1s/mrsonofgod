from aiogram.dispatcher.filters.state import StatesGroup, State

class Translation(StatesGroup):
    translate = State()

class AliLink(StatesGroup):
    waitingLink = State()