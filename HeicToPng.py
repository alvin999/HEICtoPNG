import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pyheif

def convert_heic_to_png():
    # 選擇 HEIC 檔案
    heic_path = filedialog.askopenfilename(
        title="選擇一個 HEIC 檔案",
        filetypes=[("HEIC 檔案", "*.heic *.heif")]
    )

    if not heic_path:
        return

    # 選擇儲存 PNG 檔案的路徑
    png_path = filedialog.asksaveasfilename(
        title="儲存為 PNG 檔案",
        defaultextension=".png",
        filetypes=[("PNG 檔案", "*.png")]
    )
    
    if not png_path:
        return

    try:
        # 使用 pyheif 讀取 HEIC 檔案
        heif_file = pyheif.read(heic_path)
        
        # 轉換為 Pillow 影像物件
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        
        # 儲存為 PNG 檔案
        image.save(png_path, "PNG")
        
        messagebox.showinfo("成功", "HEIC 檔案已成功轉換為 PNG！")
    
    except Exception as e:
        messagebox.showerror("錯誤", f"轉換失敗：{e}")

# 建立 GUI 視窗
root = tk.Tk()
root.title("HEIC 轉 PNG 轉換器")
root.geometry("400x150")

# 建立按鈕
convert_button = tk.Button(
    root,
    text="選擇 HEIC 檔案並轉換",
    command=convert_heic_to_png
)
convert_button.pack(pady=40)

# 執行 GUI 主迴圈
root.mainloop()