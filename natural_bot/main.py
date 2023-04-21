"""Файл для запуска бота. Содержит в себе все регистраторы приложения"""
import asyncio
from aiogram import Dispatcher
from loader import dp
from aiogram.utils import executor
from handlers import start, echo


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        []
    )


start.register_start_handlers(dp)
echo.register_echo_handlers(dp)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(echo.count_time(60))
    loop.create_task(echo.viewing_questionary_func(1800))
    loop.create_task(echo.register_func(120))
    loop.create_task(echo.like_faik_min_func(60))
    loop.create_task(echo.like_faik_day_func(60))
    executor.start_polling(dp, on_startup=set_default_commands, skip_updates=True)
