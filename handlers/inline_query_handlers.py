import hashlib
from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultCachedVoice
from handlers.decorators import check_content_of_inlinequery


# Инициализируем роутер уровня модуля
router: Router = Router()


@router.inline_query()
@check_content_of_inlinequery
async def pagination_demo(inline_query: InlineQuery,
                          audio_lst: list[tuple]):

    items_per_page = 50  # Количество результатов на одной странице.
    offset = int(inline_query.offset) if inline_query.offset else 0

    result_audio_lst = []
    try:
        for i in audio_lst:
            result_id = hashlib.md5(i[-1].encode()).hexdigest()
            inline_quer_res_voice = InlineQueryResultCachedVoice(
                id=result_id,
                voice_file_id=i[-1],
                title=f'{i[-2]} - {i[-3]}')
            result_audio_lst.append(inline_quer_res_voice)
    except TypeError:
        print('Ошибка TypeError. Вероятно, связано с "NoneType", т.е. переданный список audio_lst пуст.')
    else:

        # Ограничиваем результаты текущей "страницей"
        current_page_results = result_audio_lst[offset:offset + items_per_page]

        # Вычисляем следующий offset
        # Если это последняя страница результатов, следующий offset будет пустой строкой
        next_offset = str(offset + items_per_page) if len(audio_lst) > offset + items_per_page else ""

        await inline_query.answer(
            results=current_page_results,
            cache_time=0,
            next_offset=next_offset,
            switch_pm_parameter="t",
            switch_pm_text="АудиоМем"
        )
