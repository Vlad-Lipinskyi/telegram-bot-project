from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class FilmCallback(CallbackData, prefix="film"):
    id: int


def films_keyboard_markup(films_list: list[dict]):
    builder = InlineKeyboardBuilder()

    for index, film_data in enumerate(films_list):

        callback_data = FilmCallback(id=index)

        builder.button(
            text=film_data["name"],
            callback_data=callback_data.pack()
        )

    builder.adjust(1)
    return builder.as_markup()