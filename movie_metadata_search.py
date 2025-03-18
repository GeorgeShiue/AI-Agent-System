from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
driver = webdriver.Chrome(options = chrome_options)
driver.maximize_window()

movie_info = {}

url = "https://www.imdb.com/title/tt0133093/?ref_=fn_all_ttl_1"
driver.get(url)

rating = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/span/div/div[2]/div[1]/span[1]')
movie_info["rating"] = rating.text
# print(rating.text)

popularity = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[3]/a/span/div/div[2]/div[1]')
movie_info["popularity"] = popularity.text
# print(popularity.text)

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

print(movie_info)

response = ""
# response += f"""
# Movie Title: {movie_info["title"]}
# Link: {movie_info["link"]}
# Plot: {movie_info["plot"]}
# Casts and Characters:
# """
# for cast_and_character in movie_info["casts_and_characters"]:
#     response += f"  {cast_and_character["cast"]} playing {cast_and_character["character"]}\n"
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

print(response)

driver.quit()