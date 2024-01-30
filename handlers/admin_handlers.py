from aiogram import Router, F
from aiogram.types import Message
from config_data.config import load_config

router: Router = Router()
ADMIN_IDs = load_config().tg_bot.admin_ids


@router.message(F.voice and F.from_user.id.in_(ADMIN_IDs))
async def show_file_id_audio(message: Message):
    """
    Выводит file_id и file_unique_id файла
    :param message: Message
    :return:
    """
    if message.voice:
        await message.answer(text='file_id:')
        await message.answer(text=f'{message.voice.file_id}')
        await message.answer(text='file_unique_id:')
        await message.answer(text=f'{message.voice.file_unique_id}')
    elif message.audio:
        await message.answer(text='file_id:')
        await message.answer(text=f'{message.audio.file_id}')
        await message.answer(text='file_unique_id:')
        await message.answer(text=f'{message.audio.file_unique_id}')

