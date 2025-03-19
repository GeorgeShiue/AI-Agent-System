import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from langchain_core.tools import tool

movie_infos = []

@tool
def movie_infos_search(movie_name: str):
    """
    Input the movie name that the user is looking for and extract movies from IMDb search results and return their infos.
    The infos include the movie title, plot, cast and characters.
    """
    
    chrome_options = Options()
    driver = webdriver.Chrome(options = chrome_options)
    driver.minimize_window()
    # driver.maximize_window()

    try:
        url = "https://www.imdb.com/?ref_=nv_home"
        driver.get(url)

        input = driver.find_element(By.ID, "suggestion-search")
        input.send_keys(movie_name)

        button = driver.find_element(By.ID, "suggestion-search-button")
        button.click()
        time.sleep(0.1)

        li_elements = driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')
        for i in range(5):
            metadatas_element = li_elements[i].find_elements(By.CLASS_NAME, 'ipc-metadata-list-summary-item__li')
            metadatas = []
            for metadata_element in metadatas_element:
                metadatas.append(metadata_element.text)

            if 'TV Series' in metadatas or 'Video' in metadatas:
                # print('Skipping')
                continue

            title_element = li_elements[i].find_element(By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')
            title = title_element.text
            link = title_element.get_attribute("href")
            movie_infos.append({"title": title, "link": link, "metadatas": metadatas})

        # for movie_info in movie_infos:
        #     print(movie_info)

        for i in range(len(movie_infos)):
            # print(movie_infos[i]["title"])
            link = movie_infos[i]["link"]
            driver.get(link)

            section = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section')
            p = section.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p')
            plot_text = p.text
            movie_infos[i]["plot"] = plot_text
            if "Plot under wraps" in plot_text:
                movie_infos[i]["casts_and_characters"] = []
                continue

            try:
                section = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/div/section')
                section = section.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[4]')
                names = section.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[4]/div[2]/div[2]')
                names_list = names.text.splitlines()
            except Exception as e:
                names_list = []

            casts_and_characters = []
            for j in range(0, len(names_list), 2):
                names_list[j] = names_list[j].replace("…", "").replace("(voice)", "")
                names_list[j + 1] = names_list[j + 1].replace("…", "").replace("(voice)", "")
                casts_and_characters.append({"cast": names_list[j], "character": names_list[j + 1]})
            movie_infos[i]["casts_and_characters"] = casts_and_characters

        # for movie_info in movie_infos:
        #     print(movie_info)

        response = ""
        for movie_info in movie_infos:
            response += f"""
Movie Title: {movie_info["title"]}
Link: {movie_info["link"]}
Plot: {movie_info["plot"]}
Casts and Characters:
"""
            for cast_and_character in movie_info["casts_and_characters"]:
                response += f"  {cast_and_character["cast"]} playing {cast_and_character["character"]}\n"

        driver.quit()
        return response
    except Exception as e:
        # movie_infos = []
        driver.quit()
        return str(e)

@tool
def movie_metadata_extract(url: str):
    """
    Input the IMDb movie page URL and extract the movie title, plot, casts, characters, directors, writers, rating, popularity.
    """
    response = ""
    for movie_info in movie_infos:
        if movie_info["link"] == url:
            chrome_options = Options()
            driver = webdriver.Chrome(options = chrome_options)
            driver.maximize_window()
            
            driver.get(url)

            rating = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]')
            movie_info["rating"] = rating.text
            # print("Rating: " + rating.text)

            popularity = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[3]/a/span/div/div[2]/div[1]')
            movie_info["popularity"] = popularity.text
            # print("Popularity: " + popularity.text)

            driver.minimize_window()

            # Director
            ul_element = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[1]/div/ul')
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
            directors = []
            for li in li_elements:
                directors.append(li.text)
                # print(li.text)
            movie_info["directors"] = directors

            # Writer
            ul_element = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[2]/div/ul')
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
            writers = []
            for li in li_elements:
                writers.append(li.text)
                # print(li.text)
            movie_info["writers"] = writers

            box_office_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="title-boxoffice-section"]')

            box_office_text = box_office_div.text
            lines = box_office_text.splitlines()
            lines = lines[:-1]
            box_office = []
            for i in range(0, len(lines), 2):
                box_office.append(lines[i] + ": " + lines[i + 1])
            # print(box_office)
            movie_info["box_office"] = box_office
            
            response += f"""
Movie Title: {movie_info["title"]}
Link: {movie_info["link"]}
Plot: {movie_info["plot"]}
Casts and Characters:
"""
            for cast_and_character in movie_info["casts_and_characters"]:
                response += f"  {cast_and_character["cast"]} playing {cast_and_character["character"]}\n"
            response += "Directors: "
            for director in movie_info["directors"]:
                response += f"{director}, "
            response += "\nWriters: "
            for writer in movie_info["writers"]:
                response += f"{writer}, "
            response += "\nBox Office:\n"
            for box in movie_info["box_office"]:
                response += f"  {box}\n"
            response += f"""Rating: {movie_info["rating"]}
Popularity: {movie_info["popularity"]}
"""
            
            driver.quit()
            return response

# movie_infos_text = movie_infos_search.invoke("The Matrix")
# print(movie_infos_text)

# movie_metadata_text = movie_metadata_search.invoke("https://www.imdb.com/title/tt0133093/?ref_=fn_all_ttl_1")
# print(movie_metadata_text)