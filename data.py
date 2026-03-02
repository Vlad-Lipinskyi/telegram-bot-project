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
