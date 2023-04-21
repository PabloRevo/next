"""
Файл с моделями машины состояний
"""


from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMSignUp(StatesGroup):
    search_gender = State()
    search_age = State()
    gender = State()
    name = State()
    age = State()
    photo = State()
    social = State()
    communication_method = State()


class FSMEdit(StatesGroup):
    edit = State()

