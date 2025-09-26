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
    
    # 取得使用者已選擇的儲存資料夾路徑
    save_directory = selected_dir_path.get()
    
    # 檢查是否已選擇儲存資料夾，如果沒有則彈出警告
    if not save_directory:
        messagebox.showerror("錯誤", "請先選擇一個儲存檔案的資料夾。")
        return
    
    total_files = len(file_paths)
    successful_conversions = 0
    
    status_label.config(text="開始轉換...")
    root.update()

    for i, file_path in enumerate(file_paths, 1):
        if file_path.lower().endswith(('.heic', '.heif')):
            status_label.config(text=f"轉換進度：{i}/{total_files} - {os.path.basename(file_path)}")
            root.update()
            
            if convert_single_heic_to_png(file_path, save_directory):
                successful_conversions += 1
        else:
            messagebox.showinfo("跳過檔案", f"已跳過非 HEIC/HEIF 檔案：{os.path.basename(file_path)}")
    
    if successful_conversions == total_files:
        status_label.config(text=f"所有 {total_files} 個檔案都已成功轉換！")
        messagebox.showinfo("轉換完成", f"所有 {total_files} 個檔案都已成功轉換！")
    else:
        status_label.config(text=f"轉換完成，成功 {successful_conversions} 個，失敗 {total_files - successful_conversions} 個。")
        messagebox.showinfo("轉換完成", f"成功轉換了 {successful_conversions} 個檔案。")

def convert_single_heic_to_png(heic_path, save_dir):
    """將單個 HEIC 檔案轉換為 PNG 檔案並儲存到指定目錄下"""
    try:
        image = Image.open(heic_path)
        file_name_without_ext = os.path.splitext(os.path.basename(heic_path))[0]
        png_path = os.path.join(save_dir, f"{file_name_without_ext}.png")
        
        image.save(png_path, "PNG")
        
        return True

    except Exception as e:
        messagebox.showerror("轉換失敗", f"無法轉換檔案：{os.path.basename(heic_path)}\n錯誤訊息：{e}")
        return False

def select_save_directory():
    """打開對話框讓使用者選擇儲存資料夾，並更新 GUI"""
    directory = filedialog.askdirectory(title="選擇儲存檔案的資料夾")
    if directory:
        selected_dir_path.set(directory)

def select_and_convert_files():
    """透過檔案選擇對話框處理多個檔案"""
    file_paths = filedialog.askopenfilenames(
        title="選擇一個或多個 HEIC 檔案",
        filetypes=[("HEIC 檔案", "*.heic *.heif")]
    )
    process_files(list(file_paths))

def handle_drop(event):
    """處理檔案拖曳事件"""
    dropped_files = root.tk.splitlist(event.data)
    process_files(dropped_files)

# 建立 GUI 視窗
root = TkinterDnD.Tk()

# 先建立主視窗 root，才能創建 Tkinter 變數
# 使用 Tkinter 變數來儲存所選的儲存路徑，並能自動更新 GUI
selected_dir_path = tk.StringVar()

root.title("HEIC 轉 PNG 批量轉換器")
root.geometry("450x300") # 調整視窗高度以容納新元件

# 建立選擇資料夾按鈕
select_dir_button = tk.Button(
    root,
    text="點此選擇儲存資料夾",
    command=select_save_directory
)
select_dir_button.pack(pady=(15, 5))

# 建立顯示路徑的標籤，使用 textvariable 連結 Tkinter 變數
dir_path_label = tk.Label(
    root,
    textvariable=selected_dir_path,
    wraplength=400, # 讓長路徑可以換行
    justify="center",
    font=("Helvetica", 10),
    fg="#A0B3C2"
)
dir_path_label.pack(pady=(0, 10))

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
name_label.pack(pady=5)

# 啟用拖曳功能
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind("<<Drop>>", handle_drop)

# 執行 GUI 主迴圈
root.mainloop()