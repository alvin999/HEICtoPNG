# HEIC to PNG 轉檔工具

這是一個使用 **Python** 和 **Tkinter** 打造的圖形化使用者介面 (GUI) 應用程式，旨在提供一個直觀且高效的方式，將 HEIC 格式的圖片批次轉換為 PNG 格式。本專案核心專注於使用者體驗，讓任何人都能輕鬆完成轉檔工作。

## 核心功能

* **GUI 介面：** 提供一個易於使用的圖形化介面。
* **拖曳功能：** 支援將 HEIC 檔案直接拖曳到應用程式視窗中進行轉換。
* **檔案選擇：** 亦可透過按鈕，開啟檔案選擇器來選取檔案。
* **狀態顯示：** 轉換過程中會即時顯示進度與結果。
* **錯誤處理：** 妥善處理轉檔失敗的狀況，並以彈出視窗提示使用者。

## 技術棧

* **語言：** Python 3.x
* **GUI 函式庫：** `tkinter` 和 `tkinterdnd2`
* **影像處理：** `Pillow` 和 `pillow-heif`

## 如何執行

1.  **建立虛擬環境與安裝依賴套件**
    建議使用虛擬環境 (venv) 來管理專案依賴，以確保環境隔離與彈性。

    開啟終端機，進入專案資料夾，並執行以下指令：

    *   **建立虛擬環境：**
        ```bash
        python -m venv venv
        ```
    *   **啟動虛擬環境：**
        *   Windows: `venv\Scripts\activate`
        *   macOS / Linux: `source venv/bin/activate`
    *   **安裝依賴套件：**
        ```bash
        pip install Pillow tkinterdnd2 pillow-heif
        ```

2.  **執行程式**
    在你的終端機中，執行以下指令來啟動 GUI 程式：
    ```
    python HeicToPng.py
    ```

## 專案版本說明

本專案的核心功能（拖曳與檔案選擇）都整合在 `HeicToPng.py` 這個單一檔案中。