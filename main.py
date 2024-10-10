import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config_data.config import Config, load_config
from handlers import main_menu_handlers, all_stickers_handlers, favorite_audiolist_handlers, search_audio_handlers, \
    inline_query_handlers, admin_handlers
from middlewares.antiflood_middleware import AntifloodMiddleware
from middlewares.check_valid_inline_buttons_middlewares import CheckValidInlineButtonsMiddleware
from middlewares.subscribe_to_group_middleware import SubscribeMiddleware

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем бот и диспетчер
bot: Bot = Bot(token=config.tg_bot.token,
               parse_mode='HTML')


async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/start',
                   description='Перезапуск бота')
    ]

    await bot.set_my_commands(main_menu_commands)


async def main(bot):

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage: MemoryStorage = MemoryStorage()

    dp: Dispatcher = Dispatcher(storage=storage)

    # подключаем Middleware к диспетчеру
    dp.update.outer_middleware(SubscribeMiddleware())
    dp.update.outer_middleware(AntifloodMiddleware())
    dp.callback_query.middleware(CheckValidInlineButtonsMiddleware())

    # Регистриуем роутеры в диспетчере
    dp.include_router(main_menu_handlers.router)
    dp.include_router(all_stickers_handlers.router)
    dp.include_router(favorite_audiolist_handlers.router)
    dp.include_router(search_audio_handlers.router)
    dp.include_router(inline_query_handlers.router)
    dp.include_router(admin_handlers.router)

    # Регистрируем кнопку Menu
    dp.startup.register(set_main_menu)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot))
