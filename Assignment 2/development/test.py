from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

def search_google(keyword):
    # 初始化 Chrome WebDriver
    chrome_options = Options()
    driver = webdriver.Chrome(options = chrome_options)
    driver.maximize_window()
    try:
        # 開啟 Google 網站
        driver.get("https://www.google.com")
        
        # 找到搜尋框並輸入關鍵字
        search_box = driver.find_element(By.NAME, "q")
        time.sleep(0.5)
        search_box.send_keys(keyword)
        time.sleep(0.5)
        search_box.send_keys(Keys.RETURN)
        time.sleep(0.5)

        # 等待頁面加載完成
        time.sleep(3)
        
        # 獲取搜尋結果頁面的所有文字內容
        page_text = driver.find_element(By.TAG_NAME, "body").text
        return page_text
    finally:
        # 關閉瀏覽器
        driver.quit()


page_text = search_google("keanu reeves virtual world scifi movie")
print(page_text)