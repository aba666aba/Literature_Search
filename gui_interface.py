"""
文献检索应用的图形用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from literature_retriever import LiteratureRetriever


class LiteratureRetrieverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文献检索工具")
        self.root.geometry("800x600")
        
        self.retriever = None
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 文章输入区域
        ttk.Label(main_frame, text="请输入英文文章标题（每行一个）:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 文章标题文本区域
        self.article_text = scrolledtext.ScrolledText(main_frame, height=8, width=70)
        self.article_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 文件输入区域
        ttk.Label(main_frame, text="或选择包含文章标题的文件:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="浏览", command=self.browse_file).grid(row=0, column=1)
        
        # 选项区域
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="5")
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="后台运行（无界面）", variable=self.headless_var).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(options_frame, text="下载目录:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        dir_frame = ttk.Frame(options_frame)
        dir_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        dir_frame.columnconfigure(0, weight=1)
        
        # Save directly in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.download_dir_var = tk.StringVar(value=script_dir)
        ttk.Entry(dir_frame, textvariable=self.download_dir_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="浏览", command=self.browse_download_dir).grid(row=0, column=1)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="开始检索", command=self.start_retrieval)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_retrieval, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1)
        
        # 进度和状态
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 结果区域
        ttk.Label(main_frame, text="检索结果:").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        
        self.results_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.results_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行/列权重以支持调整大小
        main_frame.rowconfigure(8, weight=1)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择包含文章标题的文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def browse_download_dir(self):
        dir_path = filedialog.askdirectory(title="选择下载目录")
        if dir_path:
            self.download_dir_var.set(dir_path)
    
    def start_retrieval(self):
        """在单独的线程中启动检索过程"""
        # 验证输入
        articles_from_text = self.article_text.get("1.0", tk.END).strip()
        file_path = self.file_path_var.get()
        
        if not articles_from_text and not file_path:
            messagebox.showerror("错误", "请输入文章标题或选择一个文件。")
            return
        
        # 启用停止按钮并禁用开始按钮
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        # 在单独的线程中开始检索
        retrieval_thread = threading.Thread(target=self._perform_retrieval, args=(articles_from_text, file_path))
        retrieval_thread.daemon = True
        retrieval_thread.start()
    
    def stop_retrieval(self):
        """停止检索过程"""
        # 目前，我们只是禁用停止按钮
        # 在更复杂的实现中，我们需要一个标志来停止进程
        self.stop_button.config(state=tk.DISABLED)
        if self.retriever:
            self.retriever.close()
    
    def _perform_retrieval(self, articles_from_text, file_path):
        """在单独的线程中执行实际的检索"""
        try:
            # 初始化检索器
            self.retriever = LiteratureRetriever(
                headless=self.headless_var.get(),
                download_dir=self.download_dir_var.get(),
                browser='edge'
            )
            
            # 处理文章
            results = []
            
            # 如果提供了文本区域中的文章，则添加
            if articles_from_text.strip():
                article_titles = [line.strip() for line in articles_from_text.split('\n') if line.strip()]
                for i, title in enumerate(article_titles):
                    self.update_results(f"正在处理 ({i+1}/{len(article_titles)}): {title}\n")
                    result = self.retriever.retrieve_article(title)
                    status = "成功" if result else "失败"
                    path = result if result and isinstance(result, str) else "N/A"
                    results.append({'title': title, 'status': status, 'path': path})
            
            # 如果提供了文件中的文章，则添加
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_titles = [line.strip() for line in f if line.strip()]
                
                for i, title in enumerate(file_titles):
                    self.update_results(f"正在处理 ({i+1}/{len(file_titles)}): {title}\n")
                    result = self.retriever.retrieve_article(title)
                    status = "成功" if result else "失败"
                    path = result if result and isinstance(result, str) else "N/A"
                    results.append({'title': title, 'status': status, 'path': path})
            
            # 显示最终结果
            self.update_results("\n" + "="*50 + "\n检索摘要:\n" + "="*50 + "\n")
            for result in results:
                self.update_results(f"{result['status']}: {result['title']} -> {result['path']}\n")
            
            messagebox.showinfo("完成", f"检索完成！已处理 {len(results)} 篇文章。")
            
        except Exception as e:
            self.update_results(f"检索过程中发生错误: {str(e)}\n")
            messagebox.showerror("错误", f"发生错误: {str(e)}")
        
        finally:
            # 在主线程中更新UI
            self.root.after(0, self._finish_retrieval)
    
    def _finish_retrieval(self):
        """在主线程中调用以在检索完成后更新UI"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()
    
    def update_results(self, text):
        """更新结果文本组件（线程安全）"""
        self.root.after(0, lambda: self._update_results_text(text))
    
    def _update_results_text(self, text):
        """实际更新结果文本（在主线程中调用）"""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.results_text.update_idletasks()


def main():
    root = tk.Tk()
    app = LiteratureRetrieverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()