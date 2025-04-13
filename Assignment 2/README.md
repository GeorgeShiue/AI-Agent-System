# FilmSeeker_v2

`FilmSeeker_v2.py` 是一個基於多步驟計劃與執行的電影搜尋系統，旨在根據使用者的自然語言查詢，從 IMDb 中檢索相關電影資訊。此系統使用了多個模組與工具來完成搜尋、詳細資訊提取以及重新規劃的功能。

## 安裝與運行

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

## 注意事項

1. **環境變數**：請在 `.env` 文件中設置 `API_KEY`，以便與 OpenAI API 互動。
2. **IMDb 網站結構**：若 IMDb 網站結構發生變化，可能需要更新 `tools.py` 中的 XPath 選擇器。
3. **多執行緒**：程式使用非同步執行，確保 Python 版本為 3.8 或以上。

## 使用方式

### 1. 啟動程式

運行 `FilmSeeker_v2.py`：

```bash
python FilmSeeker_v2.py
```

### 2. 輸入查詢

程式會提示使用者輸入查詢，例如：

```
Please enter your query (or type 'exit' to quit): I am looking for a movie starring Keanu Reeves and the movie is about virtual reality.
```

### 3. 系統執行流程

- **計劃生成**：系統會根據輸入生成多步驟計劃。
- **執行計劃**：逐步執行計劃，並從 IMDb 獲取相關資訊。
- **重新規劃（如有需要）**：若結果不符合需求，系統會重新生成計劃。
- **結果輸出**：最終將電影資訊以結構化格式返回。

### 4. 結束程式

輸入 `exit` 結束程式。

## 功能概述

1. **查詢處理**：接受使用者的自然語言輸入，並將其轉換為可執行的計劃。
2. **計劃生成**：使用 `planner` 模組生成多步驟計劃，確保每一步都能逐步完成目標。
3. **執行計劃**：透過 `executor` 執行每個計劃步驟，並使用工具如 `movie_infos_search` 和 `movie_details_extract` 與 IMDb 互動。
4. **重新規劃**：當計劃失敗或結果不符合使用者需求時，使用 `replanner` 生成新的計劃。
5. **結果輸出**：將最終的電影資訊以結構化的方式返回給使用者。

## 專案結構

### 主要檔案

- **[FilmSeeker_v2.py](FilmSeeker_v2.py)**  
  主程式，負責整合所有模組與工具，並提供互動式的使用者介面。

- **[agents.py](agents.py)**  
  定義了 `planner`、`executor` 和 `replanner`，用於生成計劃、執行步驟以及重新規劃。

- **[tools.py](tools.py)**  
  包含與 IMDb 互動的工具函數