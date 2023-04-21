"""
Файл - содержит хэндлер для отлова сообщений вне сценария
"""
import asyncio
import datetime
import random
import string
from typing import Dict, List
from PIL import Image, ImageFont, ImageDraw
from aiogram import Dispatcher, types
from handlers.start import *
from keyboards.keyboards import buy_keyboard, pay_keyboard
from loader import logger, bot
from settings import constants
from database.models import *
from settings.settings import PAY_TOKEN


async def echo_handler(message: types.Message) -> None:
    """
    Хэндлер - оповещает бота о некорректной команде (Эхо)
    :param message: Message
    :return: None
    """
    try:
        await bot.send_message(message.from_user.id, constants.INCORRECT_INPUT)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def delete_message(user_id: int) -> None:
    """
    Функция - обрабатывает удаление сообщений
    :param user_id: int
    :return: None
    """
    try:
        message = DeleteMessage.select().where(DeleteMessage.chat_id == user_id)
        if len(message):
            for mess in message:
                if '&' in mess.message_id:
                    mes_ids = mess.message_id.split('&')
                    for elem in mes_ids:
                        try:
                            await bot.delete_message(chat_id=mess.chat_id, message_id=int(elem))
                        except Exception:
                            pass
                else:
                    try:
                        await bot.delete_message(chat_id=mess.chat_id, message_id=int(mess.message_id))
                    except Exception:
                        pass
                try:
                    mess.delete_instance()
                except Exception:
                    pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def generate_alphanum_random_string(length) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.sample(letters_and_digits, length))


async def img_red(voices, sympathy=None, flag=False) -> str:
    """
        Функция - обрабатывает фотграфии для батла
        :param
        :return: None
    """
    try:
        if sympathy:
            img1 = Image.open(f'../natural_admin/media/{sympathy.addressee.photo}')
            img2 = Image.open(f'../natural_admin/media/{voices[0].photo}')
        elif flag:
            img1 = Image.open(f'../natural_admin/media/{voices[0].addressee.photo}')
            img2 = Image.open(f'../natural_admin/media/{voices[1].addressee.photo}')
        else:
            img1 = Image.open(f'../natural_admin/media/{voices[0].photo}')
            img2 = Image.open(f'../natural_admin/media/{voices[1].photo}')
        w1, h1 = img1.size
        w2, h2 = img2.size
        if h1 > h2:
            height_percent = (h2 / float(h1))
            width_size = int(float(w1) * float(height_percent))
            img1 = img1.resize((width_size, h2))
        elif h2 > h1:
            height_percent = (h1 / float(h2))
            width_size = int(float(w2) * float(height_percent))
            img2 = img2.resize((width_size, h1))
        w1, h1 = img1.size
        w2, h2 = img2.size
        transparent = Image.new("RGBA", (w1 + w2, h1 + 70), (255, 255, 255))
        transparent.paste(img1, (0, 0), img1.convert('RGBA'))
        transparent.paste(img2, (w1, 0), img2.convert('RGBA'))
        if sympathy:
            text1 = str(sympathy.addressee.user_name) + ' ' + str(sympathy.addressee.age)
            text2 = str(voices[0].user_name) + ' ' + str(voices[0].age)
        elif flag:
            text1 = str(voices[0].addressee.user_name) + ' ' + str(voices[0].addressee.age)
            text2 = str(voices[1].addressee.user_name) + ' ' + str(voices[1].addressee.age)
        else:
            text1 = str(voices[0].user_name) + ' ' + str(voices[0].age)
            text2 = str(voices[1].user_name) + ' ' + str(voices[1].age)
        font = ImageFont.truetype('OmniglotFont.ttf', size=30)
        draw_text = ImageDraw.Draw(transparent)
        wt1, ht1 = draw_text.textsize(text1, font=font)
        wt2, ht2 = draw_text.textsize(text2, font=font)
        draw_text.text(((w1 - wt1) / 2, h1 + 20), text1, fill=('#000000'), font=font)
        draw_text.text(((w2 - wt2) / 2 + w1, h1 + 20), text2, fill=('#000000'), font=font)
        path = generate_alphanum_random_string(15)
        transparent.save(f'img/{path}.png')
        return f'img/{path}.png'
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def img_logic(sym_dict, first, second, font, first_row=None, one_img=False):
    img1 = Image.open(f'../natural_admin/media/{list(sym_dict)[first].split("&$")[0]}')
    w1, h1 = img1.size
    if one_img is False:
        img2 = Image.open(f'../natural_admin/media/{list(sym_dict)[second].split("&$")[0]}')
        w2, h2 = img2.size
        if h1 > h2:
            height_percent = (h2 / float(h1))
            width_size = int(float(w1) * float(height_percent))
            img1 = img1.resize((width_size, h2))
        elif h2 > h1:
            height_percent = (h1 / float(h2))
            width_size = int(float(w2) * float(height_percent))
            img2 = img2.resize((width_size, h1))
        w1, h1 = img1.size
        w2, h2 = img2.size
    else:
        w2, h2 = img1.size
        img2 = img1
    transparent = Image.new("RGBA", (w1 + w2, h1 + 95), (255, 255, 255))
    draw_text = ImageDraw.Draw(transparent)
    transparent.paste(img1, (0, 0), img1.convert('RGBA'))
    text11 = f"{list(sym_dict)[first].split('&$')[1]}"
    text12 = "Выбор раунда" if first_row is None else f"{await like_coroutine(sym_dict[list(sym_dict)[first]])}"
    wt11, ht11 = draw_text.textsize(text11, font=font)
    wt12, ht12 = draw_text.textsize(text12, font=font)
    draw_text.text(((w1 - wt11) / 2, h1 + 15), text11, fill=('#000000'), font=font)
    draw_text.text(((w1 - wt12) / 2, h1 + 50), text12, fill=('#000000'), font=font)
    if one_img is False:
        transparent.paste(img2, (w1, 0), img2.convert('RGBA'))
        text21 = f"{list(sym_dict)[second].split('&$')[1]}"
        text22 = f"{await like_coroutine(sym_dict[list(sym_dict)[second]])}"
        wt21, ht21 = draw_text.textsize(text21, font=font)
        wt22, ht22 = draw_text.textsize(text22, font=font)
        draw_text.text(((w2 - wt21) / 2 + w1, h1 + 15), text21, fill=('#000000'), font=font)
        draw_text.text(((w2 - wt22) / 2 + w1, h1 + 50), text22, fill=('#000000'), font=font)
    if first_row is not None:
        width_percent = first_row / float(transparent.size[0])
        height_size = int(float(transparent.size[1]) * float(width_percent))
        transparent = transparent.resize((first_row, height_size))
    return transparent


async def transparent_coroutine(tr_list: List, width: int, big_font, big_text):
    height = 140
    for elem in tr_list:
        height += elem.size[1]
    transparent = Image.new("RGBA", (width, height), (255, 255, 255))
    draw_text = ImageDraw.Draw(transparent)
    wt3, ht3 = draw_text.textsize(big_text, font=big_font)
    draw_text.text(((width - wt3) / 2, 25), big_text, fill=('#000000'), font=big_font)
    height = 140
    for elem in tr_list:
        transparent.paste(elem, (0, height), elem.convert('RGBA'))
        height += elem.size[1]
    return transparent


async def img_round_complete(sym_dict: Dict, all_round) -> str:
    """
        Функция - обрабатывает фотграфии для батла
        :param
        :return: None
    """
    try:
        font = ImageFont.truetype('OmniglotFont.ttf', size=30)
        big_font = ImageFont.truetype('OmniglotFont.ttf', size=90)
        big_text = f"Раунд {all_round}"
        if len(sym_dict) == 1:
            img1 = Image.open(f'../natural_admin/media/{list(sym_dict)[0].split("&$")[0]}')
            w1, h1 = img1.size
            transparent = Image.new("RGBA", (w1, h1 + 235), (255, 255, 255))
            transparent.paste(img1, (0, 140), img1.convert('RGBA'))
            text11 = f"{list(sym_dict)[0].split('&$')[1]}"
            text12 = "Выбор раунда"
            draw_text = ImageDraw.Draw(transparent)
            wt1, ht1 = draw_text.textsize(text11, font=font)
            wt2, ht2 = draw_text.textsize(text12, font=font)
            wt3, ht3 = draw_text.textsize(big_text, font=big_font)
            draw_text.text(((w1 - wt3) / 2, 25), big_text, fill=('#000000'), font=big_font)
            draw_text.text(((w1 - wt1) / 2, h1 + 155), text11, fill=('#000000'), font=font)
            draw_text.text(((w1 - wt2) / 2, h1 + 190), text12, fill=('#000000'), font=font)
        else:
            if len(sym_dict) == 2:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent = await transparent_coroutine([transparent1], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 3:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 2, font, transparent1.size[0], True)
                transparent = await transparent_coroutine([transparent1, transparent2], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 4:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent = await transparent_coroutine([transparent1, transparent2], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 5:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent3 = await img_logic(sym_dict, 4, 4, font, transparent1.size[0], True)
                transparent = await transparent_coroutine([transparent1, transparent2, transparent3], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 6:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent3 = await img_logic(sym_dict, 4, 5, font, transparent1.size[0])
                transparent = await transparent_coroutine([transparent1, transparent2, transparent3], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 7:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent3 = await img_logic(sym_dict, 4, 5, font, transparent1.size[0])
                transparent4 = await img_logic(sym_dict, 6, 6, font, transparent1.size[0], True)
                transparent = await transparent_coroutine([transparent1, transparent2, transparent3, transparent4], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 8:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent3 = await img_logic(sym_dict, 4, 5, font, transparent1.size[0])
                transparent4 = await img_logic(sym_dict, 6, 7, font, transparent1.size[0])
                transparent = await transparent_coroutine([transparent1, transparent2, transparent3, transparent4], transparent1.size[0], big_font, big_text)
            elif len(sym_dict) == 9:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent3 = await img_logic(sym_dict, 4, 5, font, transparent1.size[0])
                transparent4 = await img_logic(sym_dict, 6, 7, font, transparent1.size[0])
                transparent5 = await img_logic(sym_dict, 8, 8, font, transparent1.size[0], True)
                transparent = await transparent_coroutine([transparent1, transparent2, transparent3, transparent4, transparent5], transparent1.size[0], big_font, big_text)
            else:
                transparent1 = await img_logic(sym_dict, 0, 1, font)
                transparent2 = await img_logic(sym_dict, 2, 3, font, transparent1.size[0])
                transparent3 = await img_logic(sym_dict, 4, 5, font, transparent1.size[0])
                transparent4 = await img_logic(sym_dict, 6, 7, font, transparent1.size[0])
                transparent5 = await img_logic(sym_dict, 8, 9, font, transparent1.size[0])
                transparent = await transparent_coroutine([transparent1, transparent2, transparent3, transparent4, transparent5], transparent1.size[0], big_font, big_text)
        path = generate_alphanum_random_string(15)
        transparent.save(f'img/{path}.png')
        return f'img/{path}.png'
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def like_coroutine(like: int) -> str:
    if like == 1:
        return f"{like} лайк"
    elif like in [2, 3, 4]:
        return f"{like} лайка"
    else:
        return f"{like} лайков"


async def remove_restrictions(call: types.CallbackQuery) -> None:
    """
        Хэндлер - обрабатывает нажатие кнопки соглашения оплаты
        :param call: CallbackQuery
        :return: None
        """
    try:
        await delete_message(call.from_user.id)
        bot_message = await bot.send_message(
            call.from_user.id, constants.premium, reply_markup=await buy_keyboard()
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def refills_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки соглашения оплаты
    :param call: CallbackQuery
    :return: None
    """
    try:
        if call.data.endswith('1'):
            pay = key_text.settings
        else:
            pay = key_text.back_itog
        await delete_message(call.from_user.id)
        bot_message = await bot.send_invoice(
            chat_id=call.from_user.id,
            title=constants.by_title_prem,
            description=constants.by_desc_prem,
            payload='381764678',
            provider_token=PAY_TOKEN,
            currency='RUB',
            start_parameter='test',
            prices=[types.LabeledPrice(label='Руб', amount=100*100)],
            reply_markup=await pay_keyboard(pay)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery) -> None:
    """
    Хэндлер - обрабатывает оплату кристаллов. Отправляет пользователю чек об оплате.
    :param pre_checkout_query: PreCheckoutQuery
    :return: None
    """
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def process_pay_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает успешную оплату пользователя.
    :param message: types
    :return: None
    """
    try:
        user = Users.get_or_none(Users.telegram_id == message.from_user.id)
        user.premium = True
        user.save()
        await delete_message(message.from_user.id)
        bot_message = await bot.send_message(message.from_user.id, 'Оплата прошла успешно')
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        await universal_snow_profiles_handler(message)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def count_time(slp: int) -> None:
    try:
        while True:
            await asyncio.sleep(slp)
            try:
                users = Users.select().where(Users.created_at_round != None, Users.fake == False)
                utc = pytz.utc
                if len(users) > 0:
                    for user in users:
                        if (user.created_at_round + timedelta(hours=12)).replace(tzinfo=utc) < datetime.today().replace(tzinfo=utc):
                            user.created_at_round = None
                            user.round = 1
                            user.save()
                            try:
                                bot_message = await bot.send_message(
                                    user.telegram_id, constants.update_round
                                )
                                DeleteMessage(chat_id=user.telegram_id, message_id=str(bot_message.message_id)).save()
                            except Exception:
                                pass
            except Exception as error:
                logger.error('В работе бота возникло исключение', exc_info=error)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def statistics_func(user_id: int) -> None:
    current_date = datetime.today().date()
    active_user = ActiveUser.get_or_none(ActiveUser.user == user_id, ActiveUser.created_at == current_date)
    if active_user is None:
        ActiveUser(user=user_id, created_at=current_date).save()


async def viewing_questionary_func(sleeps: int) -> None:
    """
        Хэндлер - показ уведомления о анкетах
        :param sleeps: int
        :return: None
        """
    try:
        while True:
            await asyncio.sleep(sleeps)
            try:
                users = Users.select().where(Users.notifications_true == True)
                if len(users) > 0 :
                    for user in users:
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
                        if len(voices) >= 20:
                            try:
                                user.notifications_true = False
                                user.save()
                                bot_message = await bot.send_message(
                                    user.telegram_id, constants.new_anket
                                )
                                DeleteMessage(chat_id=user.telegram_id, message_id=str(bot_message.message_id)).save()
                            except:
                                pass
            except Exception as error:
                logger.error('В работе бота возникло исключение', exc_info=error)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def register_func(sleeps: int) -> None:
    """
        Хэндлер - лайки фейков
        :param sleeps: CallbackQuery
        :return: None
        """
    try:
        while True:
            try:
                users = Users.select().where(Users.sign_up != None)
                utc = pytz.utc
                if len(users) > 0:
                    for user in users:
                        try:
                            if user.sign_up.replace(tzinfo=utc) < datetime.today().replace(tzinfo=utc):
                                user.sign_up = datetime.today() + timedelta(days=1)
                                user.save()
                                bot_message = await bot.send_message(
                                    user.telegram_id, random.choice(constants.NO_REG_LIST), reply_markup=await choice_itog_round_0_keyboard()
                                )
                                DeleteMessage(chat_id=user.telegram_id, message_id=str(bot_message.message_id)).save()
                        except Exception:
                            pass
            except Exception as error:
                logger.error('В работе бота возникло исключение', exc_info=error)
            await asyncio.sleep(sleeps)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def like_faik_min_func(sleeps: int) -> None:
    """
        функция  - лайки фейков
        :param sleeps: int
        :return: None
        """
    try:
        while True:
            await asyncio.sleep(sleeps)
            try:
                users = Users.select().where(Users.push_fifteen_min != None)
                utc = pytz.utc
                if len(users):
                    minutes = random.randint(2, 5)
                    for user in users:
                        if (user.push_fifteen_min + timedelta(minutes=minutes)).replace(tzinfo=utc) < datetime.today().replace(tzinfo=utc):
                            user.sent_likes_fifteen_min += 1
                            if user.sent_likes_fifteen_min == user.number_of_likes_fifteen_min:
                                user.push_fifteen_min = None
                            else:
                                user.push_fifteen_min = datetime.today()
                            fakes = FakeLikes.select().where(FakeLikes.user == user.id)
                            search = SearchOptions.get(SearchOptions.user == user.id)
                            if len(fakes) > 0:
                                fake_list = [fakes_id.fake.id for fakes_id in fakes]
                                result = Users.select().where(Users.fake == True, Users.id.not_in(fake_list), Users.gender == search.gender).order_by(
                                    fn.Random()).limit(1)
                            else:
                                result = Users.select().where(Users.fake == True, Users.gender == search.gender).order_by(
                                    fn.Random()).limit(1)
                            FakeLikes(user=user.id, fake=result[0].id, created_at=datetime.today()).save()
                            unique = UniqueSympathy.get_or_none(UniqueSympathy.addressee == result[0].id, UniqueSympathy.sender == user.id)
                            if unique:
                                like_status = True
                            else:
                                like_status = False
                            UniqueSympathy(
                                addressee=user.id, sender=result[0].id, choice_round=False,
                                like_status=like_status
                            ).save()
                            user.save()
                            try:
                                bot_message = await bot.send_message(
                                    user.telegram_id, constants.incoming_likes
                                )
                                DeleteMessage(chat_id=user.telegram_id, message_id=str(bot_message.message_id)).save()
                            except:
                                pass

            except Exception as error:
                logger.error('В работе бота возникло исключение', exc_info=error)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def like_faik_day_func(sleeps: int) -> None:
    """
        функция  - лайки фейков
        :param sleeps: int
        :return: None
        """
    try:
        while True:
            await asyncio.sleep(sleeps)
            try:
                users = Users.select().where(Users.push_twenty_four_min != None)

                utc = pytz.utc
                if len(users):
                    for user in users:
                        if user.number_of_likes_twenty_four_min == 3:
                            hours = 3
                        elif user.number_of_likes_twenty_four_min == 2:
                            hours = 4
                        else:
                            hours = 7
                        if (user.push_twenty_four_min + timedelta(hours=hours)).replace(tzinfo=utc) < datetime.today().replace(tzinfo=utc):
                            user.sent_likes_twenty_four_min += 1
                            user.push_twenty_four_min = datetime.today() + timedelta(hours=random.randint(1, 8))
                            if user.sent_likes_twenty_four_min == user.number_of_likes_twenty_four_min:
                                user.sent_likes_twenty_four_min = 0
                                user.number_of_likes_twenty_four_min = random.randint(1, 3)
                            fakes = FakeLikes.select().where(FakeLikes.user == user.id)
                            if len(fakes) > 0:
                                fake_list = [fakes_id.fake.id for fakes_id in fakes]
                            else:
                                fake_list = []
                            search = SearchOptions.get(SearchOptions.user == user.id)
                            result = Users.select().where(Users.fake == True, Users.id.not_in(fake_list), Users.gender == search.gender).order_by(fn.Random()).limit(1)
                            if len(result) > 0:
                                FakeLikes(user=user.id, fake=result[0].id, created_at=datetime.today()).save()
                                unique = UniqueSympathy.get_or_none(UniqueSympathy.addressee == result[0].id, UniqueSympathy.sender == user.id)
                                if unique:
                                    like_status = True
                                else:
                                    like_status = False
                                UniqueSympathy(
                                    addressee=user.id, sender=result[0].id, choice_round=False,
                                    like_status=like_status
                                ).save()
                                user.save()
                                try:
                                    bot_message = await bot.send_message(
                                        user.telegram_id, constants.incoming_likes
                                    )
                                    DeleteMessage(chat_id=user.telegram_id, message_id=str(bot_message.message_id)).save()
                                except:
                                    pass
            except Exception as error:
                logger.error('В работе бота возникло исключение', exc_info=error)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def set_user_commands(user_id):
    await bot.set_my_commands(
        [
            types.BotCommand("newround", "🌟 Новый раунд"),
            types.BotCommand("inclike", "❤️Входящие лайки"),
            types.BotCommand("settings", "⚙️Настройки")
        ],
        scope=types.BotCommandScopeChat(chat_id=user_id)
    )


def register_echo_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирует все хэндлеры файла echo.py
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(echo_handler)
