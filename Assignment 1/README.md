# 🎬 FilmSeeker

FilmSeeker 是一款基於 **LangChain** 和 **Selenium** 的 AI 應用程式，能夠根據用戶的描述搜尋電影，並從 IMDb 提取相關的詳細資訊，如劇情、演員、導演、評分等。

## 📌 功能概述
1. **智能電影搜尋**：使用 AI 根據用戶輸入的關鍵字，搜尋 IMDb 並識別最相關的電影。
2. **電影資訊提取**：從 IMDb 擷取電影標題、劇情、演員、導演、編劇、評分、受歡迎程度等資訊。
3. **多步驟 AI 任務執行**：利用 LangChain **ReAct Agent** 方法，確保搜尋與資訊提取的準確性。

## 🛠️ 安裝與運行

### 1️⃣ **環境需求**
- Python 3.8+
- **Google Chrome** 瀏覽器
- **ChromeDriver** (請下載對應您 Chrome 版本的驅動程式)

### 2️⃣ **創建環境&安裝套件**
```bash
conda create --name filmseeker python=3.13
conda activate filmseeker
pip install -r requirements.txt
```

### 3️⃣ **設置 API Key**
將您的 OpenAI API Key 設定在 **.env** 文件中：
```
API_KEY=your_openai_api_key
```

## 📂 專案結構
```
📁 FilmSeeker
│── FilmSeeker.py         # 主程式，處理用戶輸入並執行 AI 代理
│── tools.py              # 包含電影搜尋與資訊提取工具
│── chromedriver.exe      # Selenium 需要的 ChromeDriver（請確保版本正確）
│── .env                  # API Key（請自行建立）
│── requirements.txt      # 依賴安裝列表
```

## 📜 主要程式說明

### **FilmSeeker.py**
- 初始化 **LangChain** 的 GPT-4o-mini 模型作為核心 AI 代理。
- 使用 `create_react_agent` 建立 AI 任務處理流程：
  1. 解析用戶輸入並推測電影名稱。
  2. 調用 `movie_infos_search()` 搜尋電影。
  3. 選擇最相關的電影並獲取 IMDb 連結。
  4. 調用 `movie_metadata_extract()` 提取電影詳細資訊。
  5. 組合資訊並返回用戶。

### **tools.py**
- `movie_infos_search(movie_name: str) → str`
  - 使用 **Selenium** 自動化 IMDb 搜尋，並獲取前五個電影結果的基本資訊（標題、劇情、演員等）。
  
- `movie_metadata_extract(url: str) → str`
  - 獲取電影的詳細資訊，包括：
    - **導演、編劇**
    - **評分、受歡迎程度**
    - **票房資訊**

---
## 📝 注意事項
- **IMDb 可能更改網站結構**，這可能導致 Selenium 抓取失敗，請確保 Xpath 選擇器仍然有效。
- **Selenium 運行時需要 ChromeDriver**，請確保 `chromedriver.exe` 與您的 Chrome 版本匹配。
- **OpenAI API Key 需要申請**，請到 [OpenAI 官方網站](https://platform.openai.com/) 註冊獲取。