from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
driver = webdriver.Chrome(options = chrome_options)
# driver.minimize_window()
driver.maximize_window()

url = "https://www.imdb.com/?ref_=nv_home"
driver.get(url)

input = driver.find_element(By.ID, "suggestion-search")
input.send_keys("The Avengers")

button = driver.find_element(By.ID, "suggestion-search-button")
button.click()
time.sleep(0.1)

movie_infos = []
li_elements = driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')
for i in range(5):
    metadatas_element = li_elements[i].find_elements(By.CLASS_NAME, 'ipc-metadata-list-summary-item__li')
    metadatas = []
    for metadata_element in metadatas_element:
        metadatas.append(metadata_element.text)

    if 'TV Series' in metadatas or 'Video' in metadatas:
        print('Skipping')
        continue

    title_element = li_elements[i].find_element(By.CSS_SELECTOR, 'a.ipc-metadata-list-summary-item__t')
    title = title_element.text
    link = title_element.get_attribute("href")
    movie_infos.append({"title": title, "link": link, "metadatas": metadatas})

for movie_info in movie_infos:
    print(movie_info)

for i in range(len(movie_infos)):
    print(movie_infos[i]["title"])
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

for movie_info in movie_infos:
    print(movie_info)

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

print(response)

driver.quit()