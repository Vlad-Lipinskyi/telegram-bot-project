import json

def get_films(
    file_path: str = "data.json", film_id: int | None = None
) -> list[dict] | dict:
    with open("data.json", "r", encoding="utf-8") as fp:
        films = json.load(fp)
        if film_id != None and film_id < len(films):
            return films[film_id]
        return films

def add_film(
    film: dict,
    file_path: str = "data.json",
):
    films = get_films(file_path=file_path, film_id=None)
    if films:
        films.append(film)
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(
                films,
                fp,
                indent=4,
                ensure_ascii=False,
            )

def delete_film(name: str):
    with open("data.json", "r", encoding="utf-8") as f:
        films = json.load(f)

    films = [film for film in films if film["name"].lower() != name.lower()]

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(films, f, ensure_ascii=False, indent=4)

import json

FILE_NAME = "data.json"

def get_films(film_id=None):
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        films = json.load(f)

    if film_id is not None:
        return films[film_id]

    return films


def save_films(films: list):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(films, f, ensure_ascii=False, indent=4)


def add_film(film: dict):
    films = get_films()
    films.append(film)
    save_films(films)


def delete_film(name: str):
    films = get_films()
    films = [film for film in films if film["name"].lower() != name.lower()]
    save_films(films)


def update_film_description(name: str, new_description: str):
    films = get_films()

    for film in films:
        if film["name"].lower() == name.lower():
            film["description"] = new_description
            break

    save_films(films)