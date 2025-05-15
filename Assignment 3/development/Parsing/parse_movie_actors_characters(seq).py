import asyncio
import json
import random
import requests

import aiohttp
from bs4 import BeautifulSoup


with open("Assignment 3/development/movie_infos.json", "r", encoding="utf-8") as f:
    movie_infos = json.load(f)

for movie_info in movie_infos:
    url = movie_info["URL"]
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    print(soup)

    cast_section = soup.find("section", {"data-testid": "title-cast"})
    cast_items = cast_section.find_all("div", {"data-testid": "title-cast-item"})

    casts_and_characters = ""
    for item in cast_items:
        actor_tag = item.find("a", {"data-testid": "title-cast-item__actor"})
        actor_name = actor_tag.text.strip() if actor_tag else "N/A"

        role_spans = item.select('ul[data-testid="cast-item-characters-list"] span')
        roles = [span.text.strip() for span in role_spans]
        role_str = ", ".join(roles) if roles else "N/A"

        casts_and_characters += f"{actor_name} plays {role_str}\n"

    print(casts_and_characters)
    print()

    movie_info["Casts_and_Characters"] = casts_and_characters

with open("Assignment 3/development/movie_infos.json", "w", encoding="utf-8") as f:
    json.dump(movie_infos, f, ensure_ascii=False, indent=4)