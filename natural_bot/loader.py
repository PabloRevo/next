"""Файл - инициализирующий бота, диспетчер, логгер и хранилище для машины состояния"""
import traceback
import requests
from typing import Optional, Callable, Coroutine, Any, Union
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from logging_config import custom_logger
from settings import settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from settings.settings import SUPPORT, CHANNEL, BOT_NAME


logger = custom_logger('bot_logger')


storage = MemoryStorage()


bot = Bot(token=settings.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


def exception_state_decorator(func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None):
    """
    Ассинхронный декоратор - обрабатывает исключения с состоянием
    :param func: Optional[Callable[..., Coroutine[Any, Any, Any]]]
    :return: Coroutine
    """
    async def wrapped(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        try:
            return await func(message, state)
        except Exception as error:
            text = f"{BOT_NAME}\n\n{traceback.format_exc()}"
            requests.get(f'https://api.telegram.org/bot{SUPPORT}/sendMessage', data={"chat_id": CHANNEL, "text": text})
            logger.error('В работе бота возникло исключение', exc_info=error)
    return wrapped


def exception_decorator(func: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None):
    """
    Ассинхронный декоратор - обрабатывает исключения без состояния
    :param func: Optional[Callable[..., Coroutine[Any, Any, Any]]]
    :return: Coroutine
    """
    async def wrapped(message: Union[types.Message, types.CallbackQuery]):
        try:
            return await func(message)
        except Exception as error:
            text = f"{BOT_NAME}\n\n{traceback.format_exc()}"
            requests.get(f'https://api.telegram.org/bot{SUPPORT}/sendMessage', data={"chat_id": CHANNEL, "text": text})
            logger.error('В работе бота возникло исключение', exc_info=error)
    return wrapped