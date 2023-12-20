import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import Config, load_config
from handlers import main_menu_handlers, all_stickers_handlers

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем бот и диспетчер
bot: Bot = Bot(token=config.tg_bot.token,
               parse_mode='HTML')

async def main(bot) -> None:

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage: MemoryStorage = MemoryStorage()

    dp: Dispatcher = Dispatcher(storage=storage)

    # Регистриуем роутеры в диспетчере
    dp.include_router(main_menu_handlers.router)
    dp.include_router(all_stickers_handlers.router)
    # dp.include_router(user_handlers_poll.router)
    # dp.include_router(user_handlers_get_price.router)
    # dp.include_router(user_handlers_services.router)
    # dp.include_router(user_handler_styles_design.router)
    # dp.include_router(admin_change_info_db.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot))




