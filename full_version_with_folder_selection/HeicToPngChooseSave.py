import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from PIL import Image
from pillow_heif import register_heif_opener

# 註冊 HEIF/HEIC 檔案的開啟器
register_heif_opener()

def process_files(file_paths):
    """
    處理檔案清單，執行批量轉換。
    此函數同時被「選擇檔案」和「拖曳」事件呼叫。
    """
    if not file_paths:
        return
    
    # 讓使用者選擇儲存資料夾
    # filedialog.askdirectory() 會打開一個資料夾選擇對話框
    messagebox.showinfo("準備好轉換", "請選擇一個資料夾來儲存轉換後的檔案。")
    save_directory = filedialog.askdirectory(title="選擇儲存轉換後檔案的資料夾")
    
    # 如果使用者點擊「取消」，函式會回傳空字串
    if not save_directory:
        status_label.config(text="已取消選取轉換資料夾")
        root.update() # 強制更新 GUI 畫面
        return
    
    total_files = len(file_paths)
    successful_conversions = 0
    
    status_label.config(text="開始轉換...")
    root.update() # 強制更新 GUI 畫面

    for i, file_path in enumerate(file_paths, 1):
        # 檢查檔案是否為 HEIC/HEIF
        if file_path.lower().endswith(('.heic', '.heif')):
            # 更新狀態標籤
            status_label.config(text=f"轉換進度：{i}/{total_files} - {os.path.basename(file_path)}")
            root.update() # 強制更新 GUI 畫面
            
            # 將新的儲存路徑傳給轉換函式
            if convert_single_heic_to_png(file_path, save_directory):
                successful_conversions += 1
        else:
            messagebox.showinfo("跳過檔案", f"已跳過非 HEIC/HEIF 檔案：{os.path.basename(file_path)}")
    
    # 在所有檔案處理完成後，顯示總結訊息
    if successful_conversions == total_files:
        status_label.config(text=f"所有 {total_files} 個檔案都已成功轉換！")
        messagebox.showinfo("轉換完成", f"所有 {total_files} 個檔案都已成功轉換！")
    else:
        status_label.config(text=f"轉換完成，成功 {successful_conversions} 個，失敗 {total_files - successful_conversions} 個。")
        messagebox.showinfo("轉換完成", f"成功轉換了 {successful_conversions} 個檔案。")

def convert_single_heic_to_png(heic_path, save_dir):
    """將單個 HEIC 檔案轉換為 PNG 檔案並儲存到指定目錄下"""
    try:
        # 讀取 HEIC 檔案
        image = Image.open(heic_path)
        
        # 建立 PNG 檔案路徑
        file_name_without_ext = os.path.splitext(os.path.basename(heic_path))[0]
        png_path = os.path.join(save_dir, f"{file_name_without_ext}.png")
        
        # 儲存為 PNG 檔案
        image.save(png_path, "PNG")
        
        return True

    except Exception as e:
        messagebox.showerror("轉換失敗", f"無法轉換檔案：{os.path.basename(heic_path)}\n錯誤訊息：{e}")
        return False

def select_and_convert_files():
    """透過檔案選擇對話框處理多個檔案"""
    file_paths = filedialog.askopenfilenames(
        title="選擇一個或多個 HEIC 檔案",
        filetypes=[("HEIC 檔案", "*.heic *.heif")]
    )
    # 將回傳的元組轉換為清單，然後交給 process_files 處理
    process_files(list(file_paths))

def handle_drop(event):
    """處理檔案拖曳事件"""
    dropped_files = root.tk.splitlist(event.data)
    # 直接將拖曳的檔案清單交給 process_files 處理
    process_files(dropped_files)

# 建立 GUI 視窗
root = TkinterDnD.Tk()
root.title("HEIC 轉 PNG 批量轉換器")
root.geometry("450x250")

# 建立一個標籤作為拖曳區
drop_label = tk.Label(
    root,
    text="將 HEIC 檔案拖曳到此處",
    font=("Helvetica", 16),
    bg="#A0B3C2",
    relief="solid",
    bd=2
)
drop_label.pack(fill="both", expand=True, padx=20, pady=20)

# 建立轉換按鈕
convert_button = tk.Button(
    root,
    text="或點此選擇 HEIC 檔案",
    command=select_and_convert_files
)
convert_button.pack(pady=10)

# 建立狀態標籤
status_label = tk.Label(
    root,
    text="等待檔案...",
    font=("Helvetica", 12),
)
status_label.pack(pady=10)

# 建立作者標籤
name_label = tk.Label(
    root,
    text="黃亞文",
    font=("Helvetica", 12),
)
# 將 name_label 放在狀態標籤下面
name_label.pack(pady=5)

# 啟用拖曳功能
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind("<<Drop>>", handle_drop)

# 執行 GUI 主迴圈
root.mainloop()