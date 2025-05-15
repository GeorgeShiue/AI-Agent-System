import asyncio
import json
import random
import requests

import aiohttp
from bs4 import BeautifulSoup

with open("Assignment 3/development/movie_infos.json", "r", encoding="utf-8") as f:
    movie_infos = json.load(f)
    
async def fetch_cast_info(session: aiohttp.ClientSession, movie_info, semaphore):
    async with semaphore:
        await asyncio.sleep(random.uniform(0.5, 2))

        url = movie_info["URL"]
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            async with session.get(url, headers=headers, timeout=10) as res:
                text = await res.text()
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            movie_info["Casts_and_Characters"] = "Fetch failed"
            return movie_info

        try:
            soup = BeautifulSoup(text, "html.parser")
            cast_section = soup.find("section", {"data-testid": "title-cast"})
            cast_items = cast_section.find_all("div", {"data-testid": "title-cast-item"})
        except Exception as e:
            print(f"⚠️ Error parsing HTML from {url}: {e}")
            movie_info["Casts_and_Characters"] = "Parse failed"
            return movie_info

        casts_and_characters = ""
        for item in cast_items:
            try:
                actor_tag = item.find("a", {"data-testid": "title-cast-item__actor"})
                actor_name = actor_tag.text.strip() if actor_tag else "N/A"

                role_spans = item.select('ul[data-testid="cast-item-characters-list"] span')
                roles = [span.text.strip() for span in role_spans]
                role_str = ", ".join(roles) if roles else "N/A"

                casts_and_characters += f"{actor_name} plays {role_str}\n"
            except Exception as e:
                print(f"⚠️ Failed to parse one cast entry: {e}")

        print(casts_and_characters)
        print()
        movie_info["Casts_and_Characters"] = casts_and_characters
        return movie_info

async def main(movie_infos):
    semaphore = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_cast_info(session, mi, semaphore) for mi in movie_infos]
        return await asyncio.gather(*tasks)
    
movie_infos = asyncio.run(main(movie_infos))

with open("Assignment 3/development/movie_infos.json", "w", encoding="utf-8") as f:
    json.dump(movie_infos, f, ensure_ascii=False, indent=4)