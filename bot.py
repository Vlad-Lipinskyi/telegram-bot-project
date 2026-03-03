import asyncio
import logging
import sys

# from os import getenv
from aiogram import Bot, Dispatcher, html, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards import films_keyboard_markup, FilmCallback
from data import get_films, add_film, delete_film, save_films
from aiogram import F
from models import Film
from aiogram.types import URLInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# from "./.env" import BOT_TOKEN as TOKEN
from dotenv import load_dotenv
from os import getenv
from commands import (
    FILMS_COMMAND,
    START_COMMAND,
    FILM_CREATE_COMMAND,
    BOT_COMMANDS,
    FILM_SEARCH_COMMAND,
    FILM_FILTER_COMMAND,
    FILM_DELETE_COMMAND,
    FILM_EDIT_COMMAND,
    FILM_RATE_COMMAND,
    FILM_RECOMMEND_COMMAND,
)

# print(films_keyboard_markup([{'name': "Harry Potter and the Philosopher's Stone", 'description': "Harry Potter and the Philosopher's Stone (also known as Harry Potter and the Sorcerer's Stone in the United States) is a 2001 fantasy film directed by Chris Columbus and produced by David Heyman, from a screenplay by Steve Kloves, based on the 1997 novel of the same name by J. K. Rowling. It is the first instalment in the Harry Potter film series. The film stars Daniel Radcliffe as Harry Potter, with Rupert Grint as Ron Weasley, and Emma Watson as Hermione Granger. Its story follows Harry's first year at Hogwarts School of Witchcraft and Wizardry as he discovers that he is a famous wizard and begins his formal wizarding education.", 'rating': 7.1, 'genre': 'Fantasy', 'actors': ['Daniel Radcliffe', 'Rupert Grint', 'Emma Watson', 'John Cleese', 'Robbie Coltrane', 'Warwick Davis', 'Richard Griffiths', 'Richard Harris', 'Ian Hart', 'John Hurt', 'Alan Rickman', 'Fiona Shaw', 'Maggie Smith', 'Julie Walters'], 'poster': 'https://upload.wikimedia.org/wikipedia/en/7/7a/Harry_Potter_and_the_Philosopher%27s_Stone_banner.jpg'}], 2, 0))

load_dotenv()


# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     """
#     This handler receives messages with `/start` command
#     """
#     # Most event objects have aliases for API methods that can be called in events' context
#     # For example if you want to answer to incoming message you can use `message.answer(...)` alias
#     # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
#     # method automatically or call API method directly via
#     # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
#     # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")
#     await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(BOT_COMMANDS)
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

# /start
@dp.message(START_COMMAND)
async def start(message: Message) -> None:
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"
        "Я перший бот Python розробника Владислава Ліпінського."
    )

# /films
@dp.message(FILMS_COMMAND)
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup,
    )


@dp.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = (
        f"Фільм: {film.name}\n"
        f"Опис: {film.description}\n"
        f"Рейтинг: {film.rating}\n"
        f"Жанр: {film.genre}\n"
        f"Актори: {', '.join(film.actors)}\n"
    )

    await callback.message.answer_photo(photo=film.poster, caption=text)

# /create_movie
class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()

@dp.message(FILM_CREATE_COMMAND)
async def film_create(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmForm.name)
    await message.answer(
        f"Введіть назву фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(
        f"Введіть опис фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.rating)
    await message.answer(
        f"Вкажіть рейтинг фільму від 0 до 10.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=float(message.text))
    await state.set_state(FilmForm.genre)
    await message.answer(
        f"Введіть жанр фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.actors)
    await message.answer(
        text=f"Введіть акторів фільму через роздільник ', '\n"
        + html.bold("Обов'язкова кома та відступ після неї."),
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
    await state.update_data(actors=[x for x in message.text.split(", ")])
    await state.set_state(FilmForm.poster)
    await message.answer(
        f"Введіть посилання на постер фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
    data = await state.update_data(poster=message.text)
    film = Film(**data)
    add_film(film.model_dump())
    await state.clear()
    await message.answer(
        f"Фільм {film.name} успішно додано!",
        reply_markup=ReplyKeyboardRemove(),
    )

# /search_movie
class MovieStates(StatesGroup):
    search_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_field = State()
    edit_description = State()
    edit_poster = State()

@router.message(FILM_SEARCH_COMMAND)
async def search_movie(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)

@router.message(MovieStates.search_query)
async def get_search_query(message: types.Message, state: FSMContext):
    query = message.text.lower()
    films = get_films()
    results = [film for film in films if query in film['name'].lower()]

    if results:
        for film in results:
            await message.answer(
                f"Знайдено: {film['name']} - {film['description']}"
            )
    else:
        await message.answer("Фільм не знайдено.")
    
    await state.clear()

# /filter_movies
@router.message(FILM_FILTER_COMMAND)
async def filter_movies(message: types.Message, state: FSMContext):
    await message.answer("Введіть жанр або рік випуску для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)

@router.message(MovieStates.filter_criteria)
async def get_filter_criteria(message: types.Message, state: FSMContext):
    criteria = message.text.lower()

    films = get_films() 
    filtered = [
        film for film in films
        if criteria in film['genre'].lower()
        or str(film.get('year', '')) == criteria
    ]

    if filtered:
        for film in filtered:
            await message.answer(
                f"Знайдено: {film['name']} - {film['description']}"
            )
    else:
        await message.answer("Фільм не знайдено за цими критеріями.")

    await state.clear()

# /delete_movie
@router.message(FILM_DELETE_COMMAND)
async def delete_movie(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)

@router.message(MovieStates.delete_query)
async def get_delete_query(message: types.Message, state: FSMContext):
    film_to_delete = message.text

    delete_film(film_to_delete)

    await message.answer("Якщо фільм існував — його видалено.")
    await state.clear()

# /edit_movie
@router.message(FILM_EDIT_COMMAND)
async def edit_movie(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)


@router.message(MovieStates.edit_query)
async def get_edit_query(message: types.Message, state: FSMContext):
    film_to_edit = message.text.lower()
    films = get_films()

    for film in films:
        if film_to_edit == film["name"].lower():
            await state.update_data(film_name=film["name"])
            await message.answer(
                "Що ви хочете змінити?\n"
                "1 - Опис\n"
                "2 - Постер"
            )
            await state.set_state(MovieStates.edit_field)
            return

    await message.answer("Фільм не знайдено.")
    await state.clear()

@router.message(MovieStates.edit_field)
async def choose_field(message: types.Message, state: FSMContext):
    if message.text == "1":
        await message.answer("Введіть новий опис:")
        await state.set_state(MovieStates.edit_description)
    elif message.text == "2":
        await message.answer("Введіть новий лінк на постер:")
        await state.set_state(MovieStates.edit_poster)
    else:
        await message.answer("Введіть 1 або 2.")

@router.message(MovieStates.edit_description)
async def update_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    film_name = data["film_name"]

    films = get_films()

    for film in films:
        if film["name"] == film_name:
            film["description"] = message.text
            break

    save_films(films)

    await message.answer("Опис оновлено.")
    await state.clear()

@router.message(MovieStates.edit_poster)
async def update_poster(message: types.Message, state: FSMContext):
    data = await state.get_data()
    film_name = data["film_name"]

    films = get_films()

    for film in films:
        if film["name"] == film_name:
            film["poster"] = message.text
            break

    save_films(films)

    await message.answer("Постер оновлено.")
    await state.clear()

# /rate_movie
class MovieRatingStates(StatesGroup):
    rate_query = State()
    set_rating = State()

@router.message(FILM_RATE_COMMAND)
async def rate_movie(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву фільму, щоб оцінити:")
    await state.set_state(MovieRatingStates.rate_query)


@router.message(MovieRatingStates.rate_query)
async def get_rate_query(message: types.Message, state: FSMContext):
    film_to_rate = message.text.lower()
    films = get_films()

    for film in films:
        if film_to_rate == film["name"].lower():
            await state.update_data(film_name=film["name"])
            await message.answer("Введіть рейтинг від 1 до 10:")
            await state.set_state(MovieRatingStates.set_rating)
            return

    await message.answer("Фільм не знайдено.")
    await state.clear()


@router.message(MovieRatingStates.set_rating)
async def set_rating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    film_name = data["film_name"]

    try:
        rating = int(message.text)

        if 1 <= rating <= 10:
            films = get_films()

            for film in films:
                if film["name"] == film_name:
                    film["rating"] = rating
                    break

            save_films(films)

            await message.answer(
                f"Рейтинг для '{film_name}' оновлено на {rating}."
            )
            await state.clear()
        else:
            await message.answer("Введіть рейтинг від 1 до 10.")

    except ValueError:
        await message.answer("Введіть число.")

# /recommend_movie
@router.message(FILM_RECOMMEND_COMMAND)
async def recommend_movie(message: types.Message):
    films = get_films()

    rated_films = [
        film for film in films
        if film.get("rating") is not None
    ]

    if rated_films:
        recommended = max(rated_films, key=lambda film: film["rating"])

        await message.answer(
            f"Рекомендуємо переглянути:\n"
            f"{recommended['name']} - {recommended['description']}\n"
            f"(Рейтинг: {recommended['rating']})"
        )
    else:
        await message.answer(
            "Немає фільмів з рейтингом для рекомендації."
        )

# Запуск
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())