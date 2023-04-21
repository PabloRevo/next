from typing import Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from keyboards import key_text


async def search_gender_keyboard(flag=False) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора пола для поиска
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if flag is False:
        return keyboard.add(
            InlineKeyboardButton(text=key_text.interested_man, callback_data=key_text.man),
            InlineKeyboardButton(text=key_text.interested_woman, callback_data=key_text.woman),
        )
    else:
        return keyboard.add(
            InlineKeyboardButton(text=key_text.interested_man, callback_data=key_text.man),
            InlineKeyboardButton(text=key_text.interested_woman, callback_data=key_text.woman),
            InlineKeyboardButton(text=key_text.back, callback_data=key_text.settings),
        )


async def search_age_keyboard(first: bool, second: bool, three: bool, foo: bool, five: bool, six: bool, flag=False) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора возраста для поиска
    :param: smile: str
    :param: first: bool
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    if flag is False:
        keyboard.add(

            InlineKeyboardButton(text='✅' + key_text.age_1 if first is True else key_text.age_1, callback_data=key_text.age_1)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_2 if second is True else key_text.age_2,
                                 callback_data=key_text.age_2)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_3 if three is True else key_text.age_3,
                                 callback_data=key_text.age_3)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_4 if foo is True else key_text.age_4,
                                 callback_data=key_text.age_4)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_5 if five is True else key_text.age_5,
                                 callback_data=key_text.age_5)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_6 if six is True else key_text.age_6,
                                 callback_data=key_text.age_6)
        )
        keyboard.add(
            InlineKeyboardButton(text=key_text.back, callback_data=key_text.back_search_gender),
            InlineKeyboardButton(text=key_text.further, callback_data=key_text.further)
        )
        return keyboard
    else:
        keyboard.add(

            InlineKeyboardButton(text='✅' + key_text.age_1 if first is True else key_text.age_1,
                                 callback_data=key_text.age_1)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_2 if second is True else key_text.age_2,
                                 callback_data=key_text.age_2)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_3 if three is True else key_text.age_3,
                                 callback_data=key_text.age_3)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_4 if foo is True else key_text.age_4,
                                 callback_data=key_text.age_4)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_5 if five is True else key_text.age_5,
                                 callback_data=key_text.age_5)
        )
        keyboard.add(
            InlineKeyboardButton(text='✅' + key_text.age_6 if six is True else key_text.age_6,
                                 callback_data=key_text.age_6)
        )
        keyboard.add(
            InlineKeyboardButton(text=key_text.back, callback_data=key_text.settings),
            InlineKeyboardButton(text=key_text.further, callback_data=key_text.further),
        )
        return keyboard


async def choice_round_0_keyboard(voices, sympathy=None, flag=False) -> InlineKeyboardMarkup:
    """
        Клавиатура для показа 0 раунда
        :param: teleg_id: str
        :return: InlineKeyboardMarkup
        """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if sympathy:
        keyboard.add(
            InlineKeyboardButton(text=sympathy.addressee.user_name + ', ' + str(sympathy.addressee.age), callback_data=f'next&{sympathy.addressee.id}'),
            InlineKeyboardButton(text=voices[0].user_name + ', ' + str(voices[0].age), callback_data=f'next&{voices[0].id}'),
            InlineKeyboardButton(text=key_text.no_choice, callback_data=key_text.no_choice)
        )
    elif flag:
        keyboard.add(
            InlineKeyboardButton(text=voices[0].addressee.user_name + ', ' + str(voices[0].addressee.age), callback_data=f'next&{voices[0].addressee.id}'),
            InlineKeyboardButton(text=voices[1].addressee.user_name + ', ' + str(voices[1].addressee.age), callback_data=f'next&{voices[1].addressee.id}'),
            InlineKeyboardButton(text=key_text.no_choice, callback_data=key_text.no_choice)
        )
    else:
        keyboard.add(
            InlineKeyboardButton(text=voices[0].user_name + ', ' + str(voices[0].age), callback_data=f'next&{voices[0].id}'),
            InlineKeyboardButton(text=voices[1].user_name + ', ' + str(voices[1].age), callback_data=f'next&{voices[1].id}'),
            InlineKeyboardButton(text=key_text.no_choice, callback_data=key_text.no_choice)
        )
    return keyboard


async def choice_itog_round_0_keyboard() -> InlineKeyboardMarkup:
    """
        Клавиатура вывод 1 раунда победителя
        :return: InlineKeyboardMarkup
        """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=key_text.start_reg, callback_data=key_text.start_reg)
    )
    return keyboard


async def reg_step_gender_keyboard(flag=False) -> InlineKeyboardMarkup:
    """
        Клавиатура первый шаг регистрации, пол юзера
        :return: InlineKeyboardMarkup
        """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if flag is False:
        keyboard.add(
            InlineKeyboardButton(text=key_text.reg_man, callback_data=key_text.reg_man),
            InlineKeyboardButton(text=key_text.reg_woman, callback_data=key_text.reg_woman)
        )
        return keyboard
    else:
        keyboard.add(
            InlineKeyboardButton(text=key_text.reg_man, callback_data=key_text.reg_man),
            InlineKeyboardButton(text=key_text.reg_woman, callback_data=key_text.reg_woman),
            InlineKeyboardButton(text=key_text.back, callback_data=key_text.settings)
        )
        return keyboard


async def reg_step_keyboard(key: str) -> InlineKeyboardMarkup:
    """
        Клавиатура второй шаг регистрации, имя юзера
        :return: InlineKeyboardMarkup
        """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=key_text.back, callback_data=key),
    )
    return keyboard


async def reply_menu_keyboard() -> ReplyKeyboardMarkup:
    """
        Клавиатура второй шаг регистрации, фото юзера
        :return: InlineKeyboardMarkup
        """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(
        KeyboardButton(text=key_text.start_menu),
        KeyboardButton(text=key_text.sender_like),
        KeyboardButton(text=key_text.settings),
    )
    return keyboard


async def push_new_like_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1)
    return keyboard.add(
        InlineKeyboardButton(key_text.sender_like, callback_data=key_text.sender_like)
    )


async def settings_keyboard() -> InlineKeyboardMarkup:
    """
        Клавиатура настроек юзера
        :return: InlineKeyboardMarkup
        """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text=key_text.settings_1, callback_data=key_text.settings_1),
        InlineKeyboardButton(text=key_text.settings_2, callback_data=key_text.settings_2),
        InlineKeyboardButton(text=key_text.settings_3, callback_data=key_text.settings_3),
        InlineKeyboardButton(text=key_text.settings_4, callback_data=key_text.settings_4),
        InlineKeyboardButton(text=key_text.settings_5, callback_data=key_text.settings_5),
        InlineKeyboardButton(text=key_text.settings_6, callback_data=key_text.settings_6),
        InlineKeyboardButton(text=key_text.settings_7, callback_data=key_text.settings_7),
        InlineKeyboardButton(text=key_text.settings_8, callback_data=key_text.settings_8),
    )
    return keyboard


async def show_complete_keyboard(user, user_round) -> InlineKeyboardMarkup:
    """
        Клавиатура показа
        :return: InlineKeyboardMarkup
        """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if user.premium is False and user.round != 4:
        return keyboard.add(
            InlineKeyboardButton(key_text.start_round.format(user_round), callback_data=key_text.start_menu),
            InlineKeyboardButton(key_text.remove_restrictions, callback_data=key_text.remove_restrictions),
        )
    elif user.premium is False and user.round == 4:
        return keyboard.add(
            InlineKeyboardButton(key_text.remove_restrictions, callback_data=key_text.remove_restrictions),
        )
    else:
        return keyboard.add(
            InlineKeyboardButton(key_text.start_round.format(user_round), callback_data=key_text.start_menu),
        )


async def buy_keyboard(flag=False, like=False, pay=0) -> None:
    """
           Клавиатура показа
           :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if flag is False and like is False:
        return keyboard.add(
            InlineKeyboardButton(key_text.price_prem, callback_data=f'{key_text.price_prem}&{pay}'),
            InlineKeyboardButton(key_text.back, callback_data=key_text.back_itog),
        )
    elif flag is True:
        return keyboard.add(
            InlineKeyboardButton(key_text.price_prem, callback_data=f'{key_text.price_prem}&{pay}'),
            InlineKeyboardButton(key_text.back, callback_data=key_text.settings),
        )
    else:
        return keyboard.add(
            InlineKeyboardButton(key_text.price_prem, callback_data=f'{key_text.price_prem}&{pay}'),
            InlineKeyboardButton(key_text.back, callback_data=key_text.sender_like),
        )


async def paginate_keyboard(num_page: int, end: int, sympathy, start=1) -> Union[InlineKeyboardMarkup, None]:
    keyboard = InlineKeyboardMarkup(row_width=3)
    if start == end:
        if sympathy.addressee.premium is False and sympathy.like_status is False:
            keyboard.add(InlineKeyboardButton(key_text.open_contact, callback_data=key_text.open_contact))
            if sympathy.choice_round is True:
                return keyboard.add(InlineKeyboardButton(key_text.choice_round, callback_data=key_text.choice_round))
            return keyboard
        elif sympathy.choice_round is True:
            return keyboard.add(InlineKeyboardButton(key_text.choice_round, callback_data=key_text.choice_round))
        return None
    elif num_page == start:
        left = end
        right = num_page + 1
    elif num_page == end:
        left = num_page - 1
        right = start
    else:
        left = num_page - 1
        right = num_page + 1
    keyboard.add(
        InlineKeyboardButton(text='⬅️', callback_data=f"paginate&{left}"),
        InlineKeyboardButton(text=f'{num_page}/{end}', callback_data=f"pass"),
        InlineKeyboardButton(text='➡️', callback_data=f"paginate&{right}"),
    )
    if sympathy.addressee.premium is False and sympathy.like_status is False:
        keyboard.add(InlineKeyboardButton(key_text.open_contact, callback_data=key_text.open_contact))
        if sympathy.choice_round is True:
            return keyboard.add(InlineKeyboardButton(key_text.choice_round, callback_data=key_text.choice_round))
        return keyboard
    elif sympathy.choice_round is True:
        return keyboard.add(InlineKeyboardButton(key_text.choice_round, callback_data=key_text.choice_round))
    return keyboard


async def social_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(key_text.choice_telegram, callback_data=key_text.choice_telegram),
        InlineKeyboardButton(key_text.choice_instagram, callback_data=key_text.choice_instagram),
        InlineKeyboardButton(key_text.choice_whatsapp, callback_data=key_text.choice_whatsapp),
        InlineKeyboardButton(key_text.other, callback_data=key_text.other),
        InlineKeyboardButton(key_text.back, callback_data=key_text.back_photo),
    )


async def pay_keyboard(key) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton('Заплатить 100,00 RUB', pay=True),
        InlineKeyboardButton(key_text.back, callback_data=key),
    )
