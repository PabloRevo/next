"""
Файл с хэндлерами старт/хэлп и регистрация
"""
import os
from datetime import timedelta
from typing import Union
import random
import string
from PIL import ImageFilter, Image
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import pytz
from database.models import *
from database.states import FSMSignUp, FSMEdit
from keyboards import key_text
from keyboards.keyboards import search_gender_keyboard, search_age_keyboard, choice_round_0_keyboard, \
    choice_itog_round_0_keyboard, reg_step_keyboard, reply_menu_keyboard, settings_keyboard, reg_step_gender_keyboard, \
    push_new_like_keyboard, show_complete_keyboard, buy_keyboard, paginate_keyboard, social_keyboard
from loader import bot, logger
from handlers.echo import delete_message, img_red, like_coroutine, img_round_complete, refills_handler, \
    remove_restrictions, pre_checkout_handler, process_pay_handler, statistics_func, set_user_commands
from settings import constants


async def start_command(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает команду /start
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        user = Users.get_or_none(Users.telegram_id == message.from_user.id)
        if user is None:
            Users(telegram_id=message.from_user.id, created_at_user=datetime.today(), telegram_login=message.from_user.username).save()
            user = Users.get_or_none(Users.telegram_id == message.from_user.id)
        else:
            await statistics_func(user.id)
            user.active_at = datetime.today()
            user.save()
        await delete_message(message.from_user.id)
        if user.count == 0:
            await FSMSignUp.search_gender.set()
            bot_message = await bot.send_message(
                message.from_user.id, constants.WELCOME, reply_markup=await search_gender_keyboard()
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        elif user.count == 1 and user.round == 1 and user.photo is None:
            sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds, Sympathy.like_status == True).order_by(Sympathy.id.desc())
            sym_dict = await ten_count_logic(sympathy, user, False)
            template = ''
            for index, elem in enumerate(sym_dict.keys()):
                if index == 0:
                    template += constants.itog_round.format(user.all_rounds - 1, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                else:
                    template += constants.itog_round_reg.format(elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
            template += constants.sympathy
            img_path = await img_round_complete(sym_dict, user.all_rounds - 1)
            bot_message = await bot.send_photo(
                message.from_user.id, open(img_path, 'rb'), template, reply_markup=await choice_itog_round_0_keyboard()
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            os.remove(img_path)
        elif user.count == 1 and user.created_at_round is not None and user.round == 4 and user.premium is False:
            """Сообщение что пользователь без преимума и прошел 3 раунда - счетчик"""
            sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds - 1, Sympathy.like_status == True).order_by(Sympathy.id.desc())
            sym_dict = await ten_count_logic(sympathy, user, False)
            template = ''
            for index, elem in enumerate(sym_dict.keys()):
                if index == 0:
                    template += constants.itog_round.format(user.all_rounds - 1, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                else:
                    template += constants.itog_round_reg.format(elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
            template += constants.itog_round_prem.format(
                "Девушкам" if sympathy[0].addressee.gender == 'Девушка' else "Парням")
            if user.round == 1 and user.premium is False:
                user.created_at_round = datetime.today()
            if user.premium is False:
                utc = pytz.utc
                template += constants.itog_round_no_prem.format(
                    3 - user.round + 1, 12 if user.round == 1 else int(((user.created_at_round + timedelta(hours=12)).replace(tzinfo=utc) - datetime.today().replace(tzinfo=utc)).total_seconds() / 60 / 60)
                )
            img_path = await img_round_complete(sym_dict, user.all_rounds - 1)
            bot_message = await bot.send_photo(
                message.from_user.id, open(img_path, 'rb'), template, reply_markup=await show_complete_keyboard(user, user.all_rounds)
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            await bot.send_message(
                message.from_user.id, constants.text_main, reply_markup=await reply_menu_keyboard()
            )
            os.remove(img_path)
        else:
            sympathy = Sympathy.select().where(Sympathy.round == user.all_rounds - 1).order_by(Sympathy.id.desc()).limit(2)
            await bot.send_message(
                message.from_user.id, constants.text_main, reply_markup=await reply_menu_keyboard()
            )
            if user.count == 1 and len(sympathy) == 0:
                """Итог пред раунда"""
                sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds - 1,
                                                   Sympathy.like_status == True).order_by(Sympathy.id.desc())
                sym_dict = await ten_count_logic(sympathy, user, False)
                template = ''
                for index, elem in enumerate(sym_dict.keys()):
                    if index == 0:
                        template += constants.itog_round.format(user.all_rounds - 1, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                    else:
                        template += constants.itog_round_reg.format(elem.split('&$')[1],
                                                                    await like_coroutine(sym_dict[elem]))
                template += constants.itog_round_prem.format(
                    "Девушкам" if sympathy[0].addressee.gender == 'Девушка' else "Парням")
                if user.round == 1 and user.premium is False:
                    user.created_at_round = datetime.today()
                if user.premium is False:
                    utc = pytz.utc
                    template += constants.itog_round_no_prem.format(
                        3 - user.round, 12 if user.round == 1 else int(((user.created_at_round + timedelta(
                            hours=12)).replace(tzinfo=utc) - datetime.today().replace(
                            tzinfo=utc)).total_seconds() / 60 / 60)
                    )
                img_path = await img_round_complete(sym_dict, user.all_rounds - 1)
                bot_message = await bot.send_photo(
                    message.from_user.id, open(img_path, 'rb'), template,
                    reply_markup=await show_complete_keyboard(user, user.all_rounds)
                )
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
                os.remove(img_path)
            else:
                photo = await img_red(voices=sympathy, flag=True)
                bot_message = await bot.send_photo(
                    message.from_user.id, open(photo, 'rb'),
                    constants.rounds.format(user.count, 10, sympathy[0].addressee.user_name, sympathy[1].addressee.user_name),
                    reply_markup=await choice_round_0_keyboard(voices=sympathy, flag=True)
                )
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
                os.remove(photo)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def search_gender_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - записывает пол и переходит к возрасту
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            data['search_gender'] = call.data
            if call.data == '👱‍♂️Парни':
                data['search_gender'] = 'Парень'
            else:
                data['search_gender'] = 'Девушка'
            await FSMSignUp.search_age.set()
            await delete_message(call.from_user.id)
            bot_message = await bot.send_message(
                call.from_user.id, constants.SEARCH_AGE, reply_markup=await search_age_keyboard(False, False, False, False, False, False)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def search_age_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - принимающий ответы пользователя по критерию возраста
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            if call.data == key_text.age_1:
                if data.get('1', None):
                    data.pop('1')
                else:
                    data['1'] = [18, 20]
            elif call.data == key_text.age_2:
                if data.get('2', None):
                    data.pop('2')
                else:
                    data['2'] = [21, 24]
            elif call.data == key_text.age_3:
                if data.get('3', None):
                    data.pop('3')
                else:
                    data['3'] = [25, 29]
            elif call.data == key_text.age_4:
                if data.get('4', None):
                    data.pop('4')
                else:
                    data['4'] = [30, 35]
            elif call.data == key_text.age_5:
                if data.get('5', None):
                    data.pop('5')
                else:
                    data['5'] = [36, 40]
            else:
                if data.get('6', None):
                    data.pop('6')
                else:
                    data['6'] = [40, 99]
            if data.get('1', None):
                first = True
            else:
                first = False
            if data.get('2', None):
                second = True
            else:
                second = False
            if data.get('3', None):
                three = True
            else:
                three = False
            if data.get('4', None):
                foo = True
            else:
                foo = False
            if data.get('5', None):
                five = True
            else:
                five = False
            if data.get('6', None):
                six = True
            else:
                six = False
            bot_message = await bot.edit_message_reply_markup(
                chat_id=call.from_user.id, message_id=call.message.message_id,  reply_markup=await search_age_keyboard(first, second, three, foo, five, six)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def first_show_logic(search, user, call, flag) -> None:
    if len(search) == 1:
        voices = Users.select().where(
            (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)
        ).order_by(fn.Random()).limit(2)
    elif len(search) == 2:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.boost == True)
        ).order_by(fn.Random()).limit(2)
    elif len(search) == 3:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == True)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.boost == True)
        ).order_by(fn.Random()).limit(2)
    else:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == True)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.boost == True)) |
            ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.boost == True)
        ).order_by(fn.Random()).limit(2)
    if len(voices) != 2:
        if len(search) == 1:
            voices = Users.select().where(
                (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age) & (Users.boost == False))
            ).order_by(fn.Random()).limit(2)
        elif len(search) == 2:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == False))
            ).order_by(fn.Random()).limit(2)

        elif len(search) == 3:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == False)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.boost == False)
            ).order_by(fn.Random()).limit(2)
        else:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == False)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.boost == False)) |
                ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.boost == False)
            ).order_by(fn.Random()).limit(2)
        if len(voices) == 0:
            flag = True
    if flag is False:
        Sympathy(addressee=voices[0].id, sender=user.id, round=user.all_rounds).save()
        Sympathy(addressee=voices[1].id, sender=user.id, round=user.all_rounds).save()
        photo = await img_red(voices)
        bot_message = await bot.send_photo(
            call.from_user.id, open(photo, 'rb'), constants.rounds.format(user.count, 10, voices[0].user_name, voices[1].user_name),
            reply_markup=await choice_round_0_keyboard(voices)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        os.remove(photo)
    return flag


async def second_show_logic(search, user, call, flag) -> None:
    all_sympathy = [sym.addressee.id for sym in Sympathy.select().where(Sympathy.sender == user.id)]
    if len(search) == 1:
        voices = Users.select().where(
            (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(2)
    elif len(search) == 2:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(2)
    elif len(search) == 3:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(2)
    else:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(2)
    if len(voices) != 2:
        if len(search) == 1:
            voices = Users.select().where(
                (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(2)
        elif len(search) == 2:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(2)
        elif len(search) == 3:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(2)
        else:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(2)
        if len(voices) == 0:
            flag = True
    if flag is False:
        Sympathy(addressee=voices[0].id, sender=user.id, round=user.all_rounds).save()
        Sympathy(addressee=voices[1].id, sender=user.id, round=user.all_rounds).save()
        photo = await img_red(voices)
        bot_message = await bot.send_photo(
            call.from_user.id, open(photo, 'rb'), constants.rounds.format(user.count, 10, voices[0].user_name, voices[1].user_name),
            reply_markup=await choice_round_0_keyboard(voices)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        os.remove(photo)
    return flag


async def snow_profiles_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - показывает анкеты пользователю
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            user = Users.get_or_none(Users.telegram_id == call.from_user.id)
            if user:
                user.count = 1
                user.save()
            search = SearchOptions.select().where(SearchOptions.user == user.id)
            if len(search) > 0:
                for elem in search:
                    elem.delete_instance()
            flag = False
            if data.get('1', None):
                flag = True
                SearchOptions(user=user.id, gender=data['search_gender'], from_age=data['1'][0], to_age=data['1'][1]).save()
            if data.get('2', None):
                flag = True
                SearchOptions(user=user.id, gender=data['search_gender'], from_age=data['2'][0], to_age=data['2'][1]).save()
            if data.get('3', None):
                flag = True
                SearchOptions(user=user.id, gender=data['search_gender'], from_age=data['3'][0], to_age=data['3'][1]).save()
            if data.get('4', None):
                flag = True
                SearchOptions(user=user.id, gender=data['search_gender'], from_age=data['4'][0], to_age=data['4'][1]).save()
            if data.get('5', None):
                flag = True
                SearchOptions(user=user.id, gender=data['search_gender'], from_age=data['5'][0], to_age=data['5'][1]).save()
            if data.get('6', None):
                flag = True
                SearchOptions(user=user.id, gender=data['search_gender'], from_age=data['6'][0], to_age=data['6'][1]).save()
            await delete_message(call.from_user.id)
            if flag:
                flag = False
                search = SearchOptions.select().where(SearchOptions.user == user.id)
                await first_show_logic(search, user, call, flag)
                await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def ten_count_logic(sympathy, user, show=True, guest=False):
    sym_dict = dict()
    unique_dict = dict()
    for symp in sympathy:
        if sym_dict.get(f"{symp.addressee.photo}&${symp.addressee.user_name}, {symp.addressee.age}", None):
            sym_dict[f"{symp.addressee.photo}&${symp.addressee.user_name}, {symp.addressee.age}"] += 1
            unique_dict[f"{symp.addressee.id}&{symp.addressee.telegram_id}"] += 1
        else:
            sym_dict[f"{symp.addressee.photo}&${symp.addressee.user_name}, {symp.addressee.age}"] = 1
            unique_dict[f"{symp.addressee.id}&{symp.addressee.telegram_id}"] = 1
    if show:
        for i, key in enumerate(unique_dict.keys()):
            like = UniqueSympathy.get_or_none(UniqueSympathy.addressee == user.id, UniqueSympathy.sender == int(key.split('&')[0]))
            if like is not None:
                like.like_status = True
                like.save()
            UniqueSympathy(
                addressee=int(key.split('&')[0]), sender=user.id, choice_round=True if i == 0 else False, like_status=True if like is not None else False,
                guest=False if guest is False else True
            ).save()
            like = UniqueSympathy.get_or_none(UniqueSympathy.addressee == int(key.split('&')[0]), UniqueSympathy.sender == user.id)
            if guest is False:
                if i == 0:
                    user.win_round += 1
                    user.save()
                try:
                    if like.like_status == True or like.choice_round == True:
                        if like.like_status is True:
                            user_message = await bot.send_message(int(key.split('&')[1]), constants.mutual_likes, reply_markup=await push_new_like_keyboard())
                            DeleteMessage(chat_id=int(key.split('&')[1]), message_id=str(user_message.message_id)).save()
                        if like.choice_round is True:
                            user_message = await bot.send_message(int(key.split('&')[1]), constants.king_round, reply_markup=await push_new_like_keyboard())
                            DeleteMessage(chat_id=int(key.split('&')[1]), message_id=str(user_message.message_id)).save()
                    else:
                        user_message = await bot.send_message(int(key.split('&')[1]), constants.incoming_likes, reply_markup=await push_new_like_keyboard())
                        DeleteMessage(chat_id=int(key.split('&')[1]), message_id=str(user_message.message_id)).save()
                except Exception:
                    pass
    return sym_dict


async def all_boost_logic(user, sympathy, call, flag):
    search = SearchOptions.select().where(SearchOptions.user == user.id)
    all_sympathy = [sym.addressee.id for sym in Sympathy.select().where(Sympathy.sender == user.id)]
    if len(search) == 1:
        voices = Users.select().where(
            (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    elif len(search) == 2:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.boost == True) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    elif len(search) == 3:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == True)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.boost == True) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    else:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == True)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == True)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.boost == True)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.boost == True) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    if len(voices) == 0:
        if len(search) == 1:
            voices = Users.select().where(
                (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        elif len(search) == 2:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.boost == False) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        elif len(search) == 3:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == False)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.boost == False) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        else:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.boost == False)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.boost == False)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.boost == False)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.boost == False) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        if len(voices) == 0:
            flag = True
    if flag is False:
        Sympathy(addressee=sympathy.addressee.id, sender=user.id, round=user.all_rounds).save()
        Sympathy(addressee=voices[0].id, sender=user.id, round=user.all_rounds).save()
        photo = await img_red(voices, sympathy)
        bot_message = await bot.send_photo(
            call.from_user.id, open(photo, 'rb'),
            constants.rounds.format(user.count, 10, sympathy.addressee.user_name, voices[0].user_name),
            reply_markup=await choice_round_0_keyboard(voices, sympathy)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        os.remove(photo)
    return flag


async def all_count_logic(user, sympathy, call, flag):
    search = SearchOptions.select().where(SearchOptions.user == user.id)
    all_sympathy = [sym.addressee.id for sym in Sympathy.select().where(Sympathy.sender == user.id)]
    if len(search) == 1:
        voices = Users.select().where(
            (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    elif len(search) == 2:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    elif len(search) == 3:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    else:
        voices = Users.select().where(
            ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.fake == False)) & (Users.id.not_in(all_sympathy)) |
            ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.fake == False) & (Users.id.not_in(all_sympathy))
        ).order_by(fn.Random()).limit(1)
    if len(voices) == 0:
        if len(search) == 1:
            voices = Users.select().where(
                (Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        elif len(search) == 2:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age))) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        elif len(search) == 3:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age))) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        else:
            voices = Users.select().where(
                ((Users.gender == search[0].gender) & (Users.age.between(search[0].from_age, search[0].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[1].gender) & (Users.age.between(search[1].from_age, search[1].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[2].gender) & (Users.age.between(search[2].from_age, search[2].to_age)) & (Users.fake == True)) & (Users.id.not_in(all_sympathy)) |
                ((Users.gender == search[3].gender) & (Users.age.between(search[3].from_age, search[3].to_age))) & (Users.fake == True) & (Users.id.not_in(all_sympathy))
            ).order_by(fn.Random()).limit(1)
        if len(voices) == 0:
            flag = True
    if flag is False:
        Sympathy(addressee=sympathy.addressee.id, sender=user.id, round=user.all_rounds).save()
        Sympathy(addressee=voices[0].id, sender=user.id, round=user.all_rounds).save()
        photo = await img_red(voices, sympathy)
        bot_message = await bot.send_photo(
            call.from_user.id, open(photo, 'rb'),
            constants.rounds.format(user.count, 10, sympathy.addressee.user_name, voices[0].user_name),
            reply_markup=await choice_round_0_keyboard(voices, sympathy)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        os.remove(photo)
    return flag


async def universal_snow_profiles_handler(call: Union[types.CallbackQuery, types.Message]) -> None:
    """
    Хэндлер - показывает анкеты пользователю
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.telegram_id == call.from_user.id)
        if user:
            await statistics_func(user.id)
            user.active_at = datetime.today()
            flag = False
            await delete_message(call.from_user.id)
            if isinstance(call, types.Message):
                call_data = call.text
                await call.delete()
            else:
                call_data = call.data
            if call_data.startswith('next'):
                voice_id = int(call_data.split('&')[1])
                sympathies = Sympathy.select().where(
                    Sympathy.addressee == voice_id, Sympathy.round == user.all_rounds
                ).order_by(Sympathy.id.desc()).limit(1)
                sympathy = sympathies.get()
                sympathy.like_status = True
                send_user = Users.get_or_none(Users.id == sympathy.addressee.id, Users.fake == False)
                if send_user:
                    send_user.get_status += 1
                    send_user.save()
                user.send_status += 1
                sympathy.save()
                if user.round == 0:
                    if user.count == 10:
                        """Тестовый раунд результат"""
                        sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds, Sympathy.like_status == True).order_by(Sympathy.id.desc())
                        sym_dict = await ten_count_logic(sympathy, user, guest=True)
                        template = ''
                        for index, elem in enumerate(sym_dict.keys()):
                            if index == 0:
                                template += constants.itog_round.format(user.all_rounds, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                            else:
                                template += constants.itog_round_reg.format(elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                        template += constants.sympathy
                        img_path = await img_round_complete(sym_dict, user.all_rounds)
                        bot_message = await bot.send_photo(
                            call.from_user.id, open(img_path, 'rb'), template, reply_markup=await choice_itog_round_0_keyboard()
                        )
                        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
                        os.remove(img_path)
                        user.sign_up = datetime.today() + timedelta(hours=1)
                        user.count = 1
                        user.round += 1
                        user.all_rounds += 1
                    else:
                        """Тестовый раунд промежуточный (1-10)"""
                        user.count += 1
                        flag = await all_boost_logic(user, sympathy, call, flag)
                else:
                    if user.count == 10:
                        """Боевые раунды результат"""
                        sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds,  Sympathy.like_status == True).order_by(Sympathy.id.desc())
                        sym_dict = await ten_count_logic(sympathy, user)
                        template = ''
                        for index, elem in enumerate(sym_dict.keys()):
                            if index == 0:
                                template += constants.itog_round.format(user.all_rounds, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                            else:
                                template += constants.itog_round_reg.format(elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                        template += constants.itog_round_prem.format("Девушкам" if sympathy[0].addressee.gender == 'Девушка' else "Парням")
                        if user.round == 1 and user.premium is False:
                            user.created_at_round = datetime.today()
                        if user.premium is False:
                            utc = pytz.utc
                            template += constants.itog_round_no_prem.format(
                                3 - user.round, 12 if user.round == 1 else int(((user.created_at_round + timedelta(hours=12)).replace(tzinfo=utc) - datetime.today().replace(tzinfo=utc)).total_seconds() / 60 / 60)
                            )
                        img_path = await img_round_complete(sym_dict, user.all_rounds)
                        user.count = 1
                        user.round += 1
                        user.all_rounds += 1
                        bot_message = await bot.send_photo(
                            call.from_user.id, open(img_path, 'rb'), template, reply_markup=await show_complete_keyboard(user, user.all_rounds)
                        )
                        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
                        os.remove(img_path)
                    else:
                        """Боевые раунды промежуточный"""
                        user.count += 1
                        flag = await all_count_logic(user, sympathy, call, flag)
            else:
                if user.count == 1:
                    sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds).order_by(Sympathy.id.desc()).limit(2)
                    if len(sympathy) < 2:
                        search = SearchOptions.select().where(SearchOptions.user == user.id)
                        flag = await second_show_logic(search, user, call, flag)
                    else:
                        if isinstance(call, types.Message) or user.round == 4:
                            sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds - 1,  Sympathy.like_status == True).order_by(Sympathy.id.desc())
                            sym_dict = await ten_count_logic(sympathy, user, False)
                            template = ''
                            for index, elem in enumerate(sym_dict.keys()):
                                if index == 0:
                                    template += constants.itog_round.format(user.all_rounds - 1, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                                else:
                                    template += constants.itog_round_reg.format(elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                            template += constants.itog_round_prem.format(
                                "Девушкам" if sympathy[0].addressee.gender == 'Девушка' else "Парням")
                            if user.premium is False:
                                utc = pytz.utc
                                template += constants.itog_round_no_prem.format(
                                    3 - user.round + 1, 12 if user.round == 1 else int(((user.created_at_round + timedelta(hours=12)).replace(tzinfo=utc) - datetime.today().replace(tzinfo=utc)).total_seconds() / 60 / 60)
                                )
                            img_path = await img_round_complete(sym_dict, user.all_rounds - 1)
                            bot_message = await bot.send_photo(
                                call.from_user.id, open(img_path, 'rb'), template, reply_markup=await show_complete_keyboard(user, user.all_rounds)
                            )
                            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
                            os.remove(img_path)
                        else:
                            photo = await img_red(voices=sympathy, flag=True)
                            bot_message = await bot.send_photo(
                                call.from_user.id, open(photo, 'rb'),
                                constants.rounds.format(user.count, 10, sympathy[0].addressee.user_name, sympathy[1].addressee.user_name),
                                reply_markup=await choice_round_0_keyboard(voices=sympathy, flag=True)
                            )
                            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
                            os.remove(photo)
                else:
                    sympathy = Sympathy.select().where(Sympathy.round == user.all_rounds).order_by(Sympathy.id.desc()).limit(2)
                    photo = await img_red(voices=sympathy, flag=True)
                    bot_message = await bot.send_photo(
                        call.from_user.id, open(photo, 'rb'),
                        constants.rounds.format(user.count, 10, sympathy[0].addressee.user_name, sympathy[1].addressee.user_name),
                        reply_markup=await choice_round_0_keyboard(voices=sympathy, flag=True)
                    )
                    DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
                    os.remove(photo)
            user.save()
            if flag is True:
                """Прописать логику-собщение когда анкеты закончились"""
                user.notifications_true = True
                user.save()
                bot_message = await bot.send_message(
                    call.from_user.id, constants.end_anket, reply_markup=await reply_menu_keyboard()
                )
                DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def no_choice_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - меняет две анкеты на новую
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.telegram_id == call.from_user.id)
        if user:
            user.count_skip += 1
            user.save()
            search = SearchOptions.select().where(SearchOptions.user == user.id)
            await delete_message(call.from_user.id)
            flag = await second_show_logic(search, user, call, False)
            if flag is True:
                user.notifications_true = True
                user.save()
                bot_message = await bot.send_message(
                    call.from_user.id, constants.end_anket, reply_markup=await reply_menu_keyboard()
                )
                DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def start_reg_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - спрашиавем пол юзера
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        await delete_message(call.from_user.id)
        await FSMSignUp.gender.set()
        Users.update({Users.step: '1'}).where(Users.telegram_id == call.from_user.id).execute()
        bot_message = await bot.send_message(
            call.from_user.id, constants.reg_step_one, reply_markup=await reg_step_gender_keyboard()
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def gender_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - спрашиавем имя юзера
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            await delete_message(call.from_user.id)
            await FSMSignUp.name.set()
            if call.data in [key_text.reg_woman, key_text.reg_man]:
                data['gender'] = 'Парень' if call.data == '👱‍♂️Парень' else 'Девушка'
            Users.update({Users.step: '2'}).where(Users.telegram_id == call.from_user.id).execute()
            bot_message = await bot.send_message(
                call.from_user.id, constants.reg_step_too, reply_markup=await reg_step_keyboard(key_text.start_reg)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def name_state(message: Union[types.Message, types.CallbackQuery], state: FSMContext) -> None:
    """
    Хэндлер - спрашиавем возраст юзера
    :param state: FSMContext
    :param message: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            await FSMSignUp.age.set()
            if isinstance(message, types.Message):
                data['name'] = message.text
            await delete_message(message.from_user.id)
            Users.update({Users.step: '3'}).where(Users.telegram_id == message.from_user.id).execute()
            bot_message = await bot.send_message(
                message.from_user.id, constants.reg_step_three, reply_markup=await reg_step_keyboard(key_text.back_name)
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def age_state(message: Union[types.Message, types.CallbackQuery], state: FSMContext) -> None:
    """
    Хэндлер - спрашиавем фото юзера
    :param state: FSMContext
    :param message: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            await delete_message(message.from_user.id)
            flag = False
            if isinstance(message, types.Message):
                if message.text.isdigit():
                    if 18 <= int(message.text) < 99:
                        await FSMSignUp.photo.set()
                        data['age'] = int(message.text)
                        flag = True
                    else:
                        """Incorrect range. Current State"""
                        bot_message = await bot.send_message(message.from_user.id, constants.incorrect_range_age)
                        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
                else:
                    """Incorrect age. Current State"""
                    bot_message = await bot.send_message(message.from_user.id, constants.incorrect_age)
                    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            else:
                flag = True
            if flag:
                await FSMSignUp.photo.set()
                Users.update({Users.step: '4'}).where(Users.telegram_id == message.from_user.id).execute()
                bot_message = await bot.send_message(
                    message.from_user.id, constants.reg_step_foo, reply_markup=await reg_step_keyboard(key_text.back_age)
                )
                DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
                await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def generate_alphanum_random_string(length) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.sample(letters_and_digits, length))


async def photo_state(message: Union[types.Message, types.CallbackQuery], state: FSMContext) -> None:
    """
    Хэндлер - записываем фото юзера
    :param state: FSMContext
    :param message: CallbackQuery
    :return: None
    """
    try:
        if isinstance(message, types.Message):
            async with state.proxy() as data:
                await message.delete()
                file_id = message.photo[len(message.photo) - 1].file_id
                file_path = (await bot.get_file(file_id)).file_path
                downloaded_file = await bot.download_file(file_path)
                path = f'{generate_alphanum_random_string(15)}.png'
                src = os.path.abspath(os.path.join('../natural_admin/media/img', path))
                data['photo'] = f'img/{path}'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.read())
                img1 = Image.open(downloaded_file)
                boxImage = img1.filter(ImageFilter.BoxBlur(20))
                boxImage.save(f'../natural_admin/media/img_blur/{path}')
                data['photo_blur'] = f'img_blur/{path}'
        await delete_message(message.from_user.id)
        await FSMSignUp.social.set()
        Users.update({Users.step: '5'}).where(Users.telegram_id == message.from_user.id).execute()
        bot_message = await bot.send_message(
            message.from_user.id, constants.reg_step_fife, reply_markup=await social_keyboard()
        )
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def social_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
        Хэндлер -
        :param state: FSMContext
        :param call: CallbackQuery
        :return: None
        """
    try:
        async with state.proxy() as data:
            data['social'] = call.data
        if call.data == key_text.choice_telegram:
            template = constants.choice_telegram
        elif call.data == key_text.choice_instagram:
            template = constants.choice_instagram
        elif call.data == key_text.choice_whatsapp:
            template = constants.choice_whatsapp
        else:
            template = constants.choice_other
        await FSMSignUp.communication_method.set()
        await delete_message(call.from_user.id)
        bot_message = await bot.send_message(
            call.from_user.id, template, reply_markup=await reg_step_keyboard(key_text.back_social)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def contact_state(message: Union[types.Message, types.CallbackQuery], state: FSMContext) -> None:
    """
    Хэндлер - спрашиавем контакт для связи  юзера
    :param state: FSMContext
    :param message: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            await message.delete()
            await delete_message(message.from_user.id)
            data['communication_method'] = message.text
            user = Users.get_or_none(Users.telegram_id == message.from_user.id)
            if user:
                user.step = '999'
                user.gender = data['gender']
                user.user_name = data['name']
                user.age = data['age']
                user.photo = data['photo']
                user.photo_blur = data['photo_blur']
                user.social = data['social']
                user.communication_method = data['communication_method']
                user.sign_up = None
                user.number_of_likes_fifteen_min = random.randint(2, 5)
                user.push_fifteen_min = datetime.today()
                user.number_of_likes_twenty_four_min = random.randint(1, 3)
                user.push_twenty_four_min = datetime.today() + timedelta(hours=random.randint(1, 8))
                await set_user_commands(message.from_user.id)
                user.save()
                unique = UniqueSympathy.select().where(UniqueSympathy.sender == user.id, UniqueSympathy.guest == True)
                if len(unique) > 0:
                    for un in unique:
                        un.guest = False
                        un.save()
                        try:
                            if un.like_status == True or un.choice_round == True:
                                if un.like_status is True:
                                    user_message = await bot.send_message(un.addressee.telegram_id,  constants.mutual_likes, reply_markup=await push_new_like_keyboard())
                                    DeleteMessage(chat_id=un.addressee.telegram_id, message_id=str(user_message.message_id)).save()
                                if un.choice_round is True:
                                    user_message = await bot.send_message(un.addressee.telegram_id, constants.king_round, reply_markup=await push_new_like_keyboard())
                                    DeleteMessage(chat_id=un.addressee.telegram_id, message_id=str(user_message.message_id)).save()
                            else:
                                user_message = await bot.send_message(un.addressee.telegram_id, constants.incoming_likes, reply_markup=await push_new_like_keyboard())
                                DeleteMessage(chat_id=un.addressee.telegram_id, message_id=str(user_message.message_id)).save()
                        except Exception:
                            pass
            bot_message = await bot.send_message(
                message.from_user.id, constants.itog_reg, reply_markup=await reply_menu_keyboard()
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def correct_setting_handler(message: types.Message, state: FSMContext) -> None:
    """
        Хэндлер - настройки
        :param state: FSMContext
        :param message: Message
        :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        if isinstance(message, types.Message):
            try:
                await message.delete()
            except:
                pass
        user = Users.get_or_none(Users.telegram_id == message.from_user.id)
        await statistics_func(user.id)
        user.active_at = datetime.today()
        search = SearchOptions.select().where(SearchOptions.user == user.id)
        search_gender = search.get().gender
        age_t = ''
        for elem in search:
            if age_t == '':
                if elem.to_age == 99:
                    age_t += f'{elem.from_age} и Старше'
                else:
                    age_t += f'{elem.from_age} - {elem.to_age}'
            else:
                if elem.to_age == 99:
                    age_t += f', {elem.from_age} и Старше'
                else:
                    age_t += f', {elem.from_age} - {elem.to_age}'
        await delete_message(message.from_user.id)
        if user.premium is False:
            text = 'Не активирован'
        else:
            text = 'Активирован'
        bot_message = await bot.send_photo(
            message.from_user.id, open(f'../natural_admin/media/{user.photo}', 'rb'), constants.settings.format(search_gender, age_t, user.gender, user.user_name, user.age, user.communication_method, text), reply_markup=await settings_keyboard()
        )
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def edit_point_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку редактирования значения автомобиля
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        user = Users.get_or_none(Users.telegram_id == call.from_user.id)
        if user:
            await delete_message(call.from_user.id)
            async with state.proxy() as data:
                data['key'] = call.data
            await FSMEdit.edit.set()
            if call.data == key_text.settings_1:
                text = constants.edit_reg_step_one_search
                keyboard = await search_gender_keyboard(True)
            elif call.data == key_text.settings_2:
                text = constants.edit_reg_step_too_search
                keyboard = await search_age_keyboard(False, False, False, False, False, False, True)
            elif call.data == key_text.settings_3:
                keyboard = await reg_step_gender_keyboard(True)
                text = constants.edit_reg_step_one
            elif call.data == key_text.settings_4:
                text = constants.edit_reg_step_two
                keyboard = await reg_step_keyboard(key_text.settings)
            elif call.data == key_text.settings_5:
                text = constants.edit_reg_step_three
                keyboard = await reg_step_keyboard(key_text.settings)
            elif call.data == key_text.settings_6:
                text = constants.edit_reg_step_five
                keyboard = await reg_step_keyboard(key_text.settings)
            elif call.data == key_text.settings_7:
                text = constants.edit_reg_step_four
                keyboard = await reg_step_keyboard(key_text.settings)
            else:
                text = constants.premium
                keyboard = await buy_keyboard(True, False, 1)
            bot_message = await bot.send_message(
                call.from_user.id, text,
                reply_markup=keyboard,
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def edit_setting_state(call: Union[types.CallbackQuery, types.Message], state: FSMContext) -> None:
    """
      Хэндлер - обрабатывает нажатие на кнопку редактирования значения автомобиля
      :param call: CallbackQuery
      :param state: FSMContext
      :return: None
      """
    try:
        user = Users.get_or_none(Users.telegram_id == call.from_user.id)
        await delete_message(call.from_user.id)
        flag = True
        marker = True
        if user:
            async with state.proxy() as data:
                if isinstance(call, types.Message):
                    await call.delete()
                    if data['key'] == key_text.settings_4:
                        user.user_name = call.text
                    elif data['key'] == key_text.settings_5:
                        user.age = call.text
                    elif data['key'] == key_text.settings_7:
                        file_id = call.photo[len(call.photo) - 1].file_id
                        file_path = (await bot.get_file(file_id)).file_path
                        downloaded_file = await bot.download_file(file_path)
                        path = f'{generate_alphanum_random_string(15)}.png'
                        src = os.path.abspath(os.path.join('../natural_admin/media/img', path))
                        data['photo'] = f'img/{path}'
                        with open(src, 'wb') as new_file:
                            new_file.write(downloaded_file.read())
                        img1 = Image.open(downloaded_file)
                        boxImage = img1.filter(ImageFilter.BoxBlur(20))
                        boxImage.save(f'../natural_admin/media/img_blur/{path}')
                        data['photo_blur'] = f'img_blur/{path}'
                        try:
                            await call.delete()
                        except:
                            pass
                        user.photo = data['photo']
                        user.photo_blur = data['photo_blur']
                    elif data['key'] == key_text.settings_6:
                        user.communication_method = call.text
                    elif data['key'] == key_text.settings_8:
                        flag = False
                        await refills_handler(call)
                    else:
                        await call.delete()
                        flag = False
                        marker = False
                else:
                    if data['key'] == key_text.settings_1:
                        if call.data == '👱‍♂️Парни':
                            gender = 'Парень'
                        else:
                            gender = 'Девушка'
                        SearchOptions.update({SearchOptions.gender: gender}).where(SearchOptions.user == user.id).execute()
                    elif data['key'] == key_text.settings_2:
                        search = SearchOptions.select().where(SearchOptions.user == user.id)
                        gender = search.get().gender
                        for elem in search:
                            elem.delete_instance()
                        if data.get('1', None):
                            SearchOptions(user=user.id, gender=gender, from_age=data['1'][0],
                                          to_age=data['1'][1]).save()
                        if data.get('2', None):
                            SearchOptions(user=user.id, gender=gender, from_age=data['2'][0],
                                          to_age=data['2'][1]).save()
                        if data.get('3', None):
                            SearchOptions(user=user.id, gender=gender, from_age=data['3'][0],
                                          to_age=data['3'][1]).save()
                        if data.get('4', None):
                            SearchOptions(user=user.id, gender=gender, from_age=data['4'][0],
                                          to_age=data['4'][1]).save()
                        if data.get('5', None):
                            SearchOptions(user=user.id, gender=gender, from_age=data['5'][0],
                                          to_age=data['5'][1]).save()
                        if data.get('6', None):
                            SearchOptions(user=user.id, gender=gender, from_age=data['6'][0],
                                          to_age=data['6'][1]).save()
                    elif data['key'] == key_text.settings_3:
                        if call.data in [key_text.reg_woman, key_text.reg_man]:
                            user.gender = 'Парень' if call.data == '👱‍♂️Парень' else 'Девушка'
                            user.save()
            user.save()
            if marker:
                await state.finish()
            if flag:
                await correct_setting_handler(call, state)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def edit_age_setting_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
      Хэндлер - обрабатывает нажатие на кнопку редактирования значения автомобиля
      :param call: CallbackQuery
      :param state: FSMContext
      :return: None
      """
    try:
        async with state.proxy() as data:
            if call.data == key_text.age_1:
                if data.get('1', None):
                    data.pop('1')
                else:
                    data['1'] = [18, 20]
            elif call.data == key_text.age_2:
                if data.get('2', None):
                    data.pop('2')
                else:
                    data['2'] = [21, 24]
            elif call.data == key_text.age_3:
                if data.get('3', None):
                    data.pop('3')
                else:
                    data['3'] = [25, 29]
            elif call.data == key_text.age_4:
                if data.get('4', None):
                    data.pop('4')
                else:
                    data['4'] = [30, 35]
            elif call.data == key_text.age_5:
                if data.get('5', None):
                    data.pop('5')
                else:
                    data['5'] = [36, 40]
            else:
                if data.get('6', None):
                    data.pop('6')
                else:
                    data['6'] = [40, 99]
            if data.get('1', None):
                first = True
            else:
                first = False
            if data.get('2', None):
                second = True
            else:
                second = False
            if data.get('3', None):
                three = True
            else:
                three = False
            if data.get('4', None):
                foo = True
            else:
                foo = False
            if data.get('5', None):
                five = True
            else:
                five = False
            if data.get('6', None):
                six = True
            else:
                six = False
            bot_message = await bot.edit_message_reply_markup(
                chat_id=call.from_user.id, message_id=call.message.message_id,
                reply_markup=await search_age_keyboard(first, second, three, foo, five, six)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def incoming_likes_handler(message: types.Message, state: FSMContext) -> None:
    """
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    if await state.get_state():
        await state.finish()
    try:
        await message.delete()
    except:
        pass
    user = Users.get_or_none(Users.telegram_id == message.from_user.id)
    end = UniqueSympathy.select().where(UniqueSympathy.addressee == user.id, UniqueSympathy.guest == False).count()
    await delete_message(message.from_user.id)
    if end > 0:
        unique = UniqueSympathy.select().where(UniqueSympathy.addressee == user.id, UniqueSympathy.guest == False).order_by(UniqueSympathy.id.desc()).paginate(1, 1)
        if user.premium is True or unique[0].like_status is True:
            photo = unique[0].sender.photo
            template = ''
            if unique[0].like_status:
                template += constants.emp_simp
            if unique[0].choice_round:
                template += constants.choice_round
            template += constants.showing_profiles_mutual.format(
                unique[0].sender.user_name, unique[0].sender.age,
                f"{unique[0].sender.social if unique[0].sender.social != 'other' else 'Другое'} {unique[0].sender.communication_method}" if unique[0].sender.communication_method is not None else "Не заполнено"
            )
        else:
            photo = unique[0].sender.photo_blur
            template = ''
            if unique[0].choice_round:
                template += constants.choice_round
            template += constants.showing_profiles_mutual.format('Скрыто', 'Скрыто',  'Скрыто')
        bot_message = await bot.send_photo(message.from_user.id, open(f'../natural_admin/media/{photo}', 'rb'), template, reply_markup=await paginate_keyboard(1, end, unique[0]))
    else:
        bot_message = await bot.send_message(message.from_user.id, constants.no_incoming_likes)
    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()


async def paginate_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку редактирования значения автомобиля
    :param call: CallbackQuery
    :return: None
    """
    user = Users.get_or_none(Users.telegram_id == call.from_user.id)
    num_page = int(call.data.split('&')[1])
    end = UniqueSympathy.select().where(UniqueSympathy.addressee == user.id, UniqueSympathy.guest == False).count()
    await delete_message(call.from_user.id)
    unique = UniqueSympathy.select().where(UniqueSympathy.addressee == user.id, UniqueSympathy.guest == False).order_by(UniqueSympathy.id.desc()).paginate(num_page, 1)
    if user.premium is True or unique[0].like_status is True:
        photo = unique[0].sender.photo
        template = ''
        if unique[0].like_status:
            template += constants.emp_simp
        if unique[0].choice_round:
            template += constants.choice_round
        template += constants.showing_profiles_mutual.format(
            unique[0].sender.user_name, unique[0].sender.age,
            f"{unique[0].sender.social if unique[0].sender.social != 'other' else 'Другое'} {unique[0].sender.communication_method}" if unique[0].sender.communication_method is not None else "Не заполнено"
        )
    else:
        photo = unique[0].sender.photo_blur
        template = ''
        if unique[0].choice_round:
            template += constants.choice_round
        template += constants.showing_profiles_mutual.format('Скрыто', 'Скрыто',  'Скрыто')
    bot_message = await bot.send_photo(call.from_user.id, open(f'../natural_admin/media/{photo}', 'rb'), template, reply_markup=await paginate_keyboard(num_page, end, unique[0]))
    DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()


async def open_contact(call: types.CallbackQuery) -> None:
    """
        Хэндлер - обрабатывает нажатие на кнопку открыть контакт
        :param call: CallbackQuery
        :return: None
    """
    try:
        bot_message = await bot.send_message(call.from_user.id, constants.buy_prem, reply_markup=await buy_keyboard(False, True, 0))
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def push_choice_round_contact(call: types.CallbackQuery) -> None:
    """
       Функция - показывает Что такое Выбор раунда
       :param call: CallbackQuery
       :return: None
       """
    try:
        await call.answer(text=constants.choice_round_push, show_alert=True)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def back_itog_handler(call: types.CallbackQuery) -> None:
    """
       Функция - показывает Что такое Выбор раунда
       :param call: CallbackQuery
       :return: None
       """
    try:
        user = Users.get_or_none(Users.telegram_id == call.from_user.id)
        if user:
            sympathy = Sympathy.select().where(Sympathy.sender == user.id, Sympathy.round == user.all_rounds - 1, Sympathy.like_status == True).order_by(Sympathy.id.desc())
            sym_dict = await ten_count_logic(sympathy, user, False)
            template = ''
            for index, elem in enumerate(sym_dict.keys()):
                if index == 0:
                    template += constants.itog_round.format(user.all_rounds - 1, elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
                else:
                    template += constants.itog_round_reg.format(elem.split('&$')[1], await like_coroutine(sym_dict[elem]))
            template += constants.itog_round_prem.format(
                "Девушкам" if sympathy[0].addressee.gender == 'Девушка' else "Парням")
            if user.round == 1 and user.premium is False:
                user.created_at_round = datetime.today()
            if user.premium is False:
                utc = pytz.utc
                template += constants.itog_round_no_prem.format(
                    3 - user.round + 1, 12 if user.round == 1 else int(((user.created_at_round + timedelta(
                        hours=12)).replace(tzinfo=utc) - datetime.today().replace(tzinfo=utc)).total_seconds() / 60 / 60)
                )
            img_path = await img_round_complete(sym_dict, user.all_rounds - 1)
            await delete_message(call.from_user.id)
            bot_message = await bot.send_photo(
                call.from_user.id, open(img_path, 'rb'), template,
                reply_markup=await show_complete_keyboard(user, user.all_rounds)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
            os.remove(img_path)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_start_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_message_handler(universal_snow_profiles_handler, commands=['newround'], state=None)
    dp.register_message_handler(correct_setting_handler, commands=['settings'], state='*')
    dp.register_message_handler(incoming_likes_handler, commands=['inclike'], state='*')
    dp.register_message_handler(correct_setting_handler, Text(equals=key_text.settings), state='*')
    dp.register_callback_query_handler(correct_setting_handler, Text(equals=key_text.settings), state='*')
    dp.register_callback_query_handler(back_itog_handler, Text(key_text.back_itog), state='*')
    dp.register_callback_query_handler(search_gender_state, state=FSMSignUp.search_gender)
    dp.register_callback_query_handler(start_command, Text(equals=key_text.back_search_gender), state=FSMSignUp.search_age)
    dp.register_callback_query_handler(
        search_age_state, Text(equals=[key_text.age_1, key_text.age_2, key_text.age_3, key_text.age_4, key_text.age_5, key_text.age_6]), state=FSMSignUp.search_age
    )
    dp.register_callback_query_handler(edit_setting_state, Text(equals=[key_text.man, key_text.woman, key_text.reg_man, key_text.reg_woman, key_text.further]), state=FSMEdit.edit)
    dp.register_message_handler(incoming_likes_handler, Text(key_text.sender_like), state='*')
    dp.register_callback_query_handler(incoming_likes_handler, Text(key_text.sender_like), state='*')
    dp.register_callback_query_handler(paginate_handler, Text(startswith='paginate'), state=None)
    dp.register_callback_query_handler(snow_profiles_handler, Text(equals=key_text.further), state='*')
    dp.register_callback_query_handler(no_choice_handler, Text(equals=key_text.no_choice), state='*')
    dp.register_callback_query_handler(push_choice_round_contact, Text(equals=key_text.choice_round), state='*')
    dp.register_callback_query_handler(universal_snow_profiles_handler, Text(equals=key_text.start_menu), state='*')
    dp.register_callback_query_handler(start_reg_handler, Text(equals=key_text.start_reg), state='*')
    dp.register_callback_query_handler(gender_state, Text(equals=[key_text.reg_man, key_text.reg_woman]), state=FSMSignUp.gender)
    dp.register_message_handler(name_state, content_types=['text'], state=FSMSignUp.name)
    dp.register_callback_query_handler(gender_state, Text(equals=key_text.back_name), state=FSMSignUp.age)
    dp.register_message_handler(age_state, content_types=['text'], state=FSMSignUp.age)
    dp.register_callback_query_handler(name_state, Text(equals=key_text.back_age), state=FSMSignUp.photo)
    dp.register_message_handler(photo_state, content_types=['photo'], state=FSMSignUp.photo)
    dp.register_callback_query_handler(age_state, Text(equals=key_text.back_photo), state=FSMSignUp.social)
    dp.register_callback_query_handler(social_state, Text(key_text.choice_list), state=FSMSignUp.social)
    dp.register_callback_query_handler(photo_state, Text(key_text.back_social), state=FSMSignUp.communication_method)
    dp.register_message_handler(contact_state, content_types=['text'], state=FSMSignUp.communication_method)
    dp.register_callback_query_handler(universal_snow_profiles_handler, Text(startswith='next'), state='*')
    dp.register_message_handler(universal_snow_profiles_handler, Text(equals=key_text.start_menu), state='*')
    dp.register_callback_query_handler(remove_restrictions, Text(equals=key_text.remove_restrictions), state='*')
    dp.register_callback_query_handler(open_contact, Text(equals=key_text.open_contact), state='*')
    dp.register_callback_query_handler(refills_handler, Text(startswith=key_text.price_prem), state='*')
    dp.register_pre_checkout_query_handler(pre_checkout_handler, lambda query: True, state=None)
    dp.register_message_handler(process_pay_handler, content_types=['successful_payment'], state=None)
    dp.register_callback_query_handler(edit_point_handler, Text(equals=key_text.setting_list), state=None)
    dp.register_message_handler(edit_setting_state, content_types=['text'], state=FSMEdit.edit)
    dp.register_message_handler(edit_setting_state, content_types=['photo'], state=FSMEdit.edit)
    dp.register_callback_query_handler(
        edit_age_setting_state, Text(equals=[key_text.age_1, key_text.age_2, key_text.age_3, key_text.age_4, key_text.age_5, key_text.age_6]), state=FSMEdit.edit
    )
