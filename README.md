# NTU Power Data Crawler (台大電力數據爬蟲)

This project provides a comprehensive crawler for fetching power-related data, including Taipower (Taiwan Power Company) generation/flow data, ancillary services settlement data, and detailed hourly power consumption for National Taiwan University (NTU) buildings and meters.

此專案提供一個綜合性的爬蟲工具，用於抓取電力相關數據，包含台電（台灣電力公司）的發電與負載數據、輔助服務結算數據，以及國立台灣大學（NTU）各館舍與電表的詳細每小時用電數據。

## How to Run (如何執行)

The system is designed for easy operation with an interactive menu.

本系統設計為透過互動式選單操作，使用方便。

To start the interactive menu, execute the following command in your terminal:

在您的終端機中執行以下指令即可啟動互動式選單：

```bash
python3 src/run.py
```

## Features (功能介紹)

Once executed, you will be presented with an interactive menu to select the specific data update you wish to perform:

執行後，您將會看到一個互動式選單，可以選擇您想要執行的數據更新項目：

### 1. Update Generator & Flow Data (Taipower) (更新台電發電與負載數據)
*   **Function (功能)**: Fetches the latest real-time power generation mix and load data from Taipower. (抓取台電最新的即時發電佔比與負載數據。)
*   **Output (輸出)**: Data is saved to `data/taipower_generators/` and `data/taipower_flow/`. (數據儲存至 `data/taipower_generators/` 和 `data/taipower_flow/`。)

### 2. Update Settlement Data (Taipower Ancillary) (更新台電輔助服務結算數據)
*   **Function (功能)**: Retrieves settlement data for Taipower's ancillary services market (e.g., pricing for regulation reserves, spinning reserves). (抓取台電輔助服務市場的結算數據（例如：調頻備轉等服務的價格）。)
*   **Output (輸出)**: Data is saved to `data/taipower_ancillary/`. (數據儲存至 `data/taipower_ancillary/`。)

### 3. Update NTU Buildings (NTU Campus Power - Key Feature) (更新台大各館舍電力數據 - 主要功能)
*   **Function (功能)**: This is the core functionality for NTU's building power consumption. It crawls hourly power data for various buildings across campus. (這是台大館舍用電的核心功能。它會爬取校園內各棟建築的每小時電力數據。)
*   **Key Enhancements (主要優化)**:
    *   **Aggregated Output (聚合式輸出)**: Instead of numerous small files, data is now aggregated into larger, category-specific CSV files (e.g., one file for all "行政" (Administration) buildings). (不再產生大量小型檔案，數據現在被聚合到更大、針對特定類別的 CSV 檔案中（例如：所有「行政」類建築物都儲存到一個檔案）。)
    *   **Incremental Updates (增量更新)**: The system automatically determines the last updated timestamp in your local files and only fetches new data, ensuring efficient updates. (系統會自動判斷您本地檔案中最新的時間戳，並只抓取新的數據，確保更新效率。)
*   **Output (輸出)**: Data is saved to `data/ntu_power/` (e.g., `行政.csv`, `宿舍.csv`, `系館.csv`, `體育.csv`, `其他.csv`). (數據儲存至 `data/ntu_power/`（例如：`行政.csv`, `宿舍.csv`, `系館.csv`, `體育.csv`, `其他.csv`）。)

### 4. Update NTU Meters (更新台大電表數據)
*   **Function (功能)**: Fetches hourly data for specific NTU meter IDs (e.g., `00A_P1_01`). (抓取特定台大電表編號（例如：`00A_P1_01`）的每小時數據。)
*   **Output (輸出)**: Data is saved as Excel files (`.xlsx`) within the `data/ntu_power/` directory. (數據儲存為 `data/ntu_power/` 目錄下的 Excel 檔案（`.xlsx`）。)

### 5. Update PV (Manual/Selenium) (更新太陽能發電數據 - 手動/Selenium)
*   **Note (注意)**: This feature requires manual interaction or specific Selenium setup and is currently skipped. (此功能需要手動操作或特定的 Selenium 設定，目前已跳過。)

### 6. Run with Custom Date Range (Historical Data Retrieval) (使用自訂日期範圍執行 - 歷史數據回補)
*   **Function (功能)**: Allows you to specify a custom start and end date to re-crawl or fill in historical data for specific modules if data gaps are identified or older data needs to be refreshed. (允許您指定自訂的開始和結束日期，以便在發現數據缺失或需要刷新舊數據時，重新爬取或補齊特定模組的歷史數據。)

### a. Run ALL (執行所有更新)
*   **Function (功能)**: Executes all available update functions sequentially (excluding the manual PV update). (依序執行所有可用的更新功能（不包括手動的太陽能發電數據更新）。)

### 0. Exit (離開)
*   **Function (功能)**: Executes all available update functions sequentially (excluding the manual PV update). (離開互動式選單。)

## Date Selection & Modes (日期選擇與模式說明)

You might wonder why you aren't asked to select a date when running a specific command (e.g., `python3 src/run.py --settlement`). This is by design:

您可能會疑惑為什麼在執行特定指令（例如：`python3 src/run.py --settlement`）時，系統沒有要求您選擇日期。這是經過特別設計的：

1.  **Interactive Mode (互動模式)**:
    *   **Command**: `python3 src/run.py` (No arguments)
    *   **Behavior**: This mode offers a menu. If you choose **Option 6 (Run with Custom Date Range)**, the system **WILL** prompt you to enter a specific start and end date. This is ideal for retrieving historical data or filling gaps.
    *   **指令**：`python3 src/run.py`（無參數）
    *   **行為**：此模式提供選單。如果您選擇 **選項 6 (Run with Custom Date Range)**，系統 **會** 提示您輸入具體的開始與結束日期。這非常適合用於回補歷史數據或填補數據空缺。

2.  **Automated Mode (自動化模式)**:
    *   **Command**: `python3 src/run.py --settlement` (With arguments)
    *   **Behavior**: This mode is designed for daily automation (e.g., cron jobs). It **automatically** detects the last date in your local data and fetches everything new up to today. It does not ask for user input to prevent the automation from hanging.
    *   **指令**：`python3 src/run.py --settlement`（帶參數）
    *   **行為**：此模式專為每日自動化（如 cron 排程）設計。它會 **自動** 偵測您本地數據的最後日期，並自動抓取從那天起到今天的所有新數據。為了防止自動化流程卡住，它不會詢問使用者輸入。

## Data Output Structure (數據輸出結構)

The `data/ntu_power/` directory now contains clean, aggregated CSV files:

`data/ntu_power/` 目錄現在包含整理過的聚合式 CSV 檔案：

```text
data/ntu_power/
├── 行政.csv    # Contains power data for all administrative buildings (e.g., library, administration building). (包含所有行政類建築（例如：圖書館、行政大樓）的電力數據。)
├── 宿舍.csv    # Contains power data for all dormitory buildings (e.g., male dorms, female dorms). (包含所有宿舍建築（例如：男一舍、女九舍）的電力數據。)
├── 系館.csv    # Contains power data for all departmental buildings (e.g., Electrical Engineering, Chemistry Building). (包含所有系館建築（例如：電機館、化學館）的電力數據。)
├── 體育.csv    # Contains power data for all sports facilities. (包含所有體育設施的電力數據。)
└── 其他.csv    # Contains power data for other miscellaneous facilities. (包含其他雜項設施的電力數據。)
```

**Note (注意)**: All CSV files are now saved with `utf-8-sig` encoding, which ensures proper display of Chinese characters when opened in spreadsheet applications like Microsoft Excel. Column headers are now correctly identified with their respective building names.

所有 CSV 檔案現在都以 `utf-8-sig` 編碼儲存，這確保了在像 Microsoft Excel 等試算表應用程式中打開時，中文字符能正常顯示，不會出現亂碼。欄位標題現在也已正確識別為對應的建築名稱。

## Advanced Usage: Automated Execution (進階用法：自動化執行)

For automating daily updates (e.g., via cron jobs), you can run specific update functions directly without the interactive menu by passing command-line arguments:

為了自動化每日更新（例如：透過 cron 排程），您可以直接透過傳遞命令列參數來執行特定的更新功能，而無需進入互動式選單：

*   To run all updates: (執行所有更新：)
    ```bash
    python3 src/run.py --all
    ```
*   To update only NTU buildings: (只更新台大館舍：)
    ```bash
    python3 src/run.py --buildings
    ```
*   To update only Taipower generators/flow data: (只更新台電發電與負載數據：)
    ```bash
    python3 src/run.py --generators
    ```
*   To update only Taipower settlement data: (只更新台電輔助服務結算數據：)
    ```bash
    python3 src/run.py --settlement
    ```
*   To update only NTU meters: (只更新台大電表數據：)
    ```bash
    python3 src/run.py --meters
    ```