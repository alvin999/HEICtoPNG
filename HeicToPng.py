# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from PIL import Image
from pillow_heif import register_heif_opener
import threading
import multiprocessing as mp
import time
import sys

# 註冊 HEIF/HEIC 檔案的開啟器
register_heif_opener()

# --- 多程序工作函數 (Worker Function) ---

def worker_convert_single_heic_to_png(heic_path):
    # 此函數定義在類別外部，以確保它可以被子程序正確地序列化 (pickling)。
    # multiprocessing 在跨程序傳遞任務時需要對目標函數進行序列化，而頂層函數 (top-level function) 是最容易被序列化的。
    """
    將單個 HEIC 檔案轉換為 PNG 檔案。此函數將由多程序池呼叫。
    """
    try:
        image = Image.open(heic_path)
        file_dir = os.path.dirname(heic_path)
        file_name_without_ext = os.path.splitext(os.path.basename(heic_path))[0]
        png_path = os.path.join(file_dir, f"{file_name_without_ext}.png")
        image.save(png_path, "PNG")
        return (True, None, heic_path)
    except Exception as e:
        return (False, str(e), heic_path)

# --- GUI 應用程式類別 (Main Application Class) ---

class HEICToPNGApp:
    def __init__(self, master):
        self.master = master
        master.title("HEIC 轉 PNG 批次轉換器 (多核心加速版)")
        master.geometry("450x380")
        master.config(bg="#f0f0f0")

        # 內部狀態變數，取代全域變數
        self.is_converting = False
        self.is_animating = False
        self.conversion_results = []
        self.conversion_thread = None
        self.progress_text = "等待檔案..."

        # GUI 元件
        self._setup_ui()
        
    def _setup_ui(self):
        # 設定樣式
        try:
            self.master.option_add("*Font", "Inter 12")
        except:
            self.master.option_add("*Font", "Helvetica 12")

        # 建立拖曳區
        self.drop_label = tk.Label(
            self.master,
            text="將 HEIC 檔案拖曳到此處\n或點擊下方按鈕",
            font=("Helvetica", 16, "bold"),
            fg="#333333",
            bg="#DDEAF5",
            relief="groove",
            bd=2,
            pady=30,
            cursor="hand2"
        )
        self.drop_label.pack(fill="both", expand=True, padx=20, pady=20)

        # 建立轉換按鈕
        self.convert_button = tk.Button(
            self.master,
            text="選擇 HEIC 檔案並開始轉換",
            font=("Helvetica", 12),
            bg="#4F86F7", 
            fg="white",
            activebackground="#3A6CBE",
            activeforeground="black",
            relief="raised",
            bd=3,
            command=self.select_and_convert_files
        )
        self.convert_button.pack(pady=(0, 10), ipadx=10, ipady=5)

        # 建立進度條
        self.progress_bar = ttk.Progressbar(
            self.master,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress_bar.pack(pady=(5, 10), padx=20) 

        # 建立狀態標籤
        self.status_label = tk.Label(
            self.master,
            text=self.progress_text,
            font=("Helvetica", 12),
            bg="#f0f0f0",
            fg="#555555"
        )
        self.status_label.pack(pady=5)

        # 啟用拖曳功能
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.handle_drop)

    # --- GUI 事件處理函式 ---

    def select_and_convert_files(self):
        if self.is_converting:
            messagebox.showwarning("忙碌中", "請等待當前批次轉換完成。")
            return
        
        self.status_label.config(text="正在初始化...")
        self.progress_text = "正在初始化..."
        self.progress_bar.config(value=0)
        self.master.update()
            
        file_paths = filedialog.askopenfilenames(
            title="選擇一個或多個 HEIC 檔案",
            filetypes=[("圖片檔案", "*.heic *.heif"), ("所有檔案", "*.*")]
        )
        if file_paths:
            self.start_conversion_thread(list(file_paths))
        else:
            self._reset_state()

    def handle_drop(self, event):
        if self.is_converting:
            messagebox.showwarning("忙碌中", "請等待當前批次轉換完成。")
            return
        
        self.status_label.config(text="正在初始化...")
        self.progress_text = "正在初始化..."
        self.progress_bar.config(value=0)
        self.master.update()
            
        dropped_files = self.master.tk.splitlist(event.data)
        
        if dropped_files:
            self.start_conversion_thread(dropped_files)
        else:
            self._reset_state()
            
    def _reset_state(self):
        self.is_converting = False
        self.is_animating = False
        self.progress_text = "等待檔案..."
        self.status_label.config(text=self.progress_text)
        self.progress_bar.config(value=0)

    # --- 執行緒管理函式 ---

    def start_conversion_thread(self, file_paths):
        heic_paths = [
            p for p in file_paths
            if p.lower().endswith(('.heic', '.heif')) and os.path.exists(p)
        ]

        skipped_count = len(file_paths) - len(heic_paths)
        if skipped_count > 0:
            self.master.after(0, lambda: messagebox.showinfo("跳過檔案", f"已跳過 {skipped_count} 個非 HEIC/HEIF 檔案。"))

        if not heic_paths:
            self.master.after(0, lambda: self.status_label.config(text="沒有 HEIC 檔案需要轉換。"))
            self.is_converting = False
            return

        self.is_converting = True
        self.is_animating = True
        total_files = len(heic_paths)
        
        self.master.after(0, self.animate_spinner, 0)

        self.conversion_thread = threading.Thread(
            target=self.run_multiprocess_conversion,
            args=(heic_paths, total_files) # 建立一個獨立的執行緒來管理多程序轉換任務，避免長時間操作阻塞 GUI 主執行緒，從而防止視窗無回應。
        )
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def run_multiprocess_conversion(self, heic_paths, total_files):
        # 圖片轉換是 CPU 密集型任務。此處使用 multiprocessing 來繞過 Python 的全域直譯器鎖 (GIL)，
        # 實現真正的平行處理，以充分利用多核心 CPU 的效能。
        num_processes = min(mp.cpu_count(), 4) 
        
        with mp.Pool(processes=num_processes) as pool:
            tasks = [(p,) for p in heic_paths]
            # 使用 starmap_async 以非同步方式提交任務。
            # 這允許當前的管理執行緒可以不被阻塞，並能透過迴圈持續監控轉換進度。
            async_result = pool.starmap_async(worker_convert_single_heic_to_png, tasks)
            
            while not async_result.ready():
                current_completed = total_files - async_result._number_left
                # Tkinter 的 GUI 元件不是執行緒安全的 (thread-safe)。所有 UI 的更新操作都必須透過
                # self.master.after() 方法，將其排程到主執行緒中執行，以避免競爭條件和程式崩潰。
                self.master.after(0, self.update_status_and_spinner, current_completed, total_files)
                time.sleep(0.1)

            self.conversion_results = async_result.get()
        
        self.master.after(0, self.finalize_gui_update, self.conversion_results, total_files)
        
    def animate_spinner(self, spinner_index):
        if not self.is_animating:
            return

        spinner_chars = ['|', '/', '-', '\\']
        self.status_label.config(text=f"{self.progress_text} {spinner_chars[spinner_index]}")

        next_index = (spinner_index + 1) % len(spinner_chars)
        self.master.after(100, self.animate_spinner, next_index)
        
    def update_status_and_spinner(self, current_completed, total_files):
        percent_complete = int((current_completed / total_files) * 100)
        self.progress_bar.config(value=percent_complete)
        self.progress_text = f"總進度：{percent_complete}% ({current_completed}/{total_files} 個檔案已完成)"

    def finalize_gui_update(self, results, total_files):
        self.is_converting = False
        self.is_animating = False
        
        successful_count = sum(1 for success, _, _ in results if success)
        failed_count = total_files - successful_count
        
        self.progress_bar.config(value=100)
        
        final_message = f"轉換完成！\n成功：{successful_count} 個\n失敗：{failed_count} 個"
        
        self.status_label.config(text=f"轉換完成，成功 {successful_count} 個，失敗 {failed_count} 個。")
        messagebox.showinfo("轉換完成", final_message)

        if failed_count > 0:
            error_messages = "\n".join([
                f"- 檔案 {os.path.basename(path)} 失敗: {err}"
                for success, err, path in results if not success
            ])
            messagebox.showwarning("部分轉換失敗", f"以下檔案轉換失敗：\n{error_messages[:500]}...")
            
        self.master.after(1500, self._reset_state)

# --- 主程式進入點 ---

if __name__ == '__main__':
    # 在 Windows 平台上，使用 multiprocessing 必須將啟動子程序的程式碼放在 if __name__ == '__main__': 區塊內。
    # 這是因為 Windows 缺乏 fork()，子程序會重新 import 主腳本，此舉可防止無限遞迴地創建子程序。
    # freeze_support() 則是用於支援打包成獨立執行檔 (例如使用 PyInstaller)。
    if sys.platform.startswith('win'):
        mp.freeze_support()
        
    root = TkinterDnD.Tk()
    app = HEICToPNGApp(root)
    root.mainloop()