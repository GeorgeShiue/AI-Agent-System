# 🎬 FilmSeeker v3

**FilmSeeker v3** 是一個基於 [LangGraph](https://github.com/langchain-ai/langgraph)、[LangChain](https://www.langchain.com/)、IMDb 資料與工具鏈構建的智能電影搜尋與推理代理系統。它能理解自然語言輸入，自動規劃、執行並回應與電影相關的問題（如找出特定演員的電影、根據描述找片名、查詢劇情、演員、導演、票房等）。

---

## 🚀 安裝與運行

### 1️⃣ 環境需求

* Python 3.8+
* **Google Chrome** 瀏覽器
* **ChromeDriver** (請下載對應您 Chrome 版本的駕動程式)

### 2️⃣ 創建環境&安裝套件

```bash
conda create --name filmseeker python=3.10
conda activate filmseeker
pip install -r requirements.txt
```

### 3️⃣ 設置 API Key

將您的 OpenAI API Key 設定在 **.env** 文件中：

```
API_KEY=your_openai_api_key
```

---

## 🔹 使用方式

### 1. 啟動系統

執行 `FilmSeeker_v3.py`：

```bash
python FilmSeeker_v3.py
```

### 2. 輸入查詢

系統會請你輸入一個電影相關的問題，例如：

```
Please enter your query (or type 'exit' to quit): I am looking for a movie starring Keanu Reeves and the movie is about virtual reality.
```

### 3. 系統執行流程

* **Plan Lookup**：首先在 vectorstore 中搜尋是否已有相似輸入的過去 plan
* **Planner**：如果無相關記錄，則重新生成解決步驟
* **Executor**：執行 plan 中的工作，采用 IMDb 工具
* **Replanner**：如果結果不合理或出現錯誤，將重新規劃 plan
* **Final Response**：展示最終的結果

---

## 📚 功能概述

1. **Query Processing**：分析使用者的輸入，轉換為 plan 可執行的内容
2. **Plan Generation**：使用 planner agent 製作多步驟件準備處理
3. **Execute Plan**：透過 executor agent 執行所建設的解決步驟，帶出 IMDb 資料
4. **Replan When Needed**：當結果不合理時，使用 replanner 重新計畫
5. **Plan Memory**：將使用者輸入與 plan 儲存在向量資料庫，供下次類似問題擁有記憶

---

## 📂 計畫組成

```
FilmSeeker_v3/
├── FilmSeeker_v3.py       ［主執行程式，啟動主系統］
├── agents.py              ［計畫、執行、重新計畫的代理設計］
├── graph.py               ［使用 LangGraph 定義的系統流程］
├── tools.py               ［與 IMDb 互動的工具，執行搜尋/解析］
├── movie_infos_db/        ［儲存電影資料的向量 DB］
└── plan_documents_db/     ［儲存過去計畫資料的向量 DB］
```

---

## 🔧 IMDB 工具 (位於 `tools.py`)

| 工具名稱                    | 功能描述                            |
| ----------------------- | ------------------------------- |
| `movie_name_generate`   | 根據用戶輸入推測電影名稱（向量搜尋）              |
| `movie_infos_search`    | 使用 Selenium 搜尋 IMDb 並取得電影網頁總覽資料 |
| `movie_metadata_search` | 擁有 IMDb 連結後，重點提取導演、劇本、票房、評分等資料  |