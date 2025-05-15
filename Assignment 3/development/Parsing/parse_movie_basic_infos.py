import time
import json

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
driver = webdriver.Chrome(options = chrome_options)

url = "https://www.imdb.com/search/title/?title_type=feature&sort=num_votes,desc"
driver.get(url)

time.sleep(0.1)

def get_li_elements():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    ul_element = soup.find("ul", class_="ipc-metadata-list")
    li_elements = ul_element.find_all("li", class_="ipc-metadata-list-summary-item")
    return li_elements

# def try_click_see_more(driver: webdriver.Chrome, timeout=10):
#     try:
#         # 等待按鈕可見並可點擊
#         button = WebDriverWait(driver, timeout).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ipc-see-more__button"))
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
#         button.click()
#         print("Clicked 'See More' successfully.")
#     except Exception as e:
#         print(f"Failed to click 'See More': {e}")

def wait_and_get_li_elements(driver, timeout=10):
    for _ in range(5):  # 最多重試 5 次
        try:
            return get_li_elements()
        except Exception:
            print("Waiting for new items to load...")
            time.sleep(2)
    raise Exception("Failed to load new elements after retries.")

movie_infos = []
li_elements = get_li_elements()
for i in range(3000):
    imdb_url = "https://www.imdb.com"
    li = li_elements[i]
    
    title = li.find("h3", class_="ipc-title__text")
    print(f"Title: {title.text}")
    plot = li.find("div", class_="ipc-html-content-inner-div")
    print(f"Plot: {plot.text if plot else 'No plot'}")
    url = li.find("a", class_="ipc-title-link-wrapper")
    print(f"URL: {imdb_url + url['href']}")
    print()

    info_dict = {"Title": title.text, "Plot": plot.text if plot else 'No plot', "URL": imdb_url + url['href']}
    movie_infos.append(info_dict)

    with open("Assignment 3/development/movie_infos.json", "w", encoding="utf-8") as f:
        json.dump(movie_infos, f, ensure_ascii=False, indent=4)

    if (i+1) % 50 == 0:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
        time.sleep(2)

        see_more_button = driver.find_element(By.CSS_SELECTOR, "button.ipc-see-more__button")
        see_more_button.click()
        time.sleep(4)

        li_elements = wait_and_get_li_elements(driver)

driver.quit()