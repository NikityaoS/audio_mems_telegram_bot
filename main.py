import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from db_logic import mongo_client

from config_data.config import Config, load_config
from handlers import main_menu_handlers, all_stickers_handlers, favorite_audiolist_handlers
# from db_logic import mongo_client


# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем бот и диспетчер
bot: Bot = Bot(token=config.tg_bot.token,
               parse_mode='HTML')

async def main(bot):

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage: MemoryStorage = MemoryStorage()

    dp: Dispatcher = Dispatcher(storage=storage)

    # Регистриуем роутеры в диспетчере
    dp.include_router(main_menu_handlers.router)
    dp.include_router(all_stickers_handlers.router)
    dp.include_router(favorite_audiolist_handlers.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main(bot))





