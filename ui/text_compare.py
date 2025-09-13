#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本对比工具模块
提供文本差异检测和高亮显示功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import difflib


class TextCompareWindow:
    """文本对比窗口类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.left_text = None
        self.right_text = None
        self.compare_stats_label = None
        
    def open(self):
        """打开文本对比窗口"""
        if self.window and self.window.winfo_exists():
            # 如果窗口已存在，则将其提到前台
            self.window.lift()
            self.window.focus()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("文本对比工具")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="文本对比工具", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 创建对比区域
        compare_frame = ttk.Frame(main_frame)
        compare_frame.pack(fill='both', expand=True)
        compare_frame.columnconfigure(0, weight=1)
        compare_frame.columnconfigure(1, weight=1)
        compare_frame.rowconfigure(0, weight=1)
        
        # 左侧文本框
        left_frame = ttk.LabelFrame(compare_frame, text="文本A", padding="5")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        self.left_text = tk.Text(left_frame, wrap=tk.WORD, font=('Consolas', 10))
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.left_text.yview)
        self.left_text.configure(yscrollcommand=left_scrollbar.set)
        
        self.left_text.grid(row=0, column=0, sticky="nsew")
        left_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 右侧文本框
        right_frame = ttk.LabelFrame(compare_frame, text="文本B", padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.right_text = tk.Text(right_frame, wrap=tk.WORD, font=('Consolas', 10))
        right_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.right_text.yview)
        self.right_text.configure(yscrollcommand=right_scrollbar.set)
        
        self.right_text.grid(row=0, column=0, sticky="nsew")
        right_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 同步滚动
        self.left_text.bind('<MouseWheel>', self._sync_scroll)
        self.right_text.bind('<MouseWheel>', self._sync_scroll)
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(10, 0))
        
        # 按钮组
        button_group = ttk.Frame(control_frame)
        button_group.pack()
        
        ttk.Button(button_group, text="🔄 开始对比", command=self.start_compare, style='Success.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_group, text="📋 清空文本", command=self.clear_texts, style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_group, text="📁 加载文件", command=self.load_texts_from_files, style='Info.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_group, text="❌ 关闭", command=self.window.destroy, style='Danger.TButton').pack(side='left')
        
        # 统计信息标签
        self.compare_stats_label = ttk.Label(control_frame, text="", foreground='gray')
        self.compare_stats_label.pack(pady=(10, 0))
        
        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """窗口关闭时的处理"""
        if self.window:
            self.window.destroy()
            self.window = None
    
    def _sync_scroll(self, event):
        """同步滚动两个文本框"""
        if event.widget == self.left_text:
            self.right_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.left_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def start_compare(self):
        """开始文本对比"""
        text_a = self.left_text.get("1.0", tk.END).strip()
        text_b = self.right_text.get("1.0", tk.END).strip()
        
        if not text_a or not text_b:
            messagebox.showwarning("警告", "请先输入要对比的文本")
            return
        
        # 清空之前的高亮
        self.clear_highlights()
        
        # 执行对比
        differences = self.compare_texts(text_a, text_b)
        
        # 应用高亮
        self.apply_highlights(differences)
        
        # 更新统计信息
        self.update_stats(differences)
    
    def compare_texts(self, text_a, text_b):
        """对比两个文本，返回差异信息 - 使用行级对比算法"""
        lines_a = text_a.splitlines(keepends=True)
        lines_b = text_b.splitlines(keepends=True)
        
        differences = {
            'added': [],      # 在B中新增的行位置
            'removed': [],    # 在A中删除的行位置
            'modified': [],   # 修改的行位置
            'same': []        # 相同的行位置
        }
        
        # 使用 SequenceMatcher 进行行级对比
        matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # 相同的行
                for i in range(i1, i2):
                    differences['same'].append(i)
            elif tag == 'delete':
                # 删除的行
                for i in range(i1, i2):
                    differences['removed'].append(i)
            elif tag == 'insert':
                # 新增的行
                for j in range(j1, j2):
                    differences['added'].append(j)
            elif tag == 'replace':
                # 替换的行
                for i in range(i1, i2):
                    differences['removed'].append(i)
                for j in range(j1, j2):
                    differences['added'].append(j)
        
        return differences
    
    def apply_highlights(self, differences):
        """应用行级高亮显示"""
        # 配置标签样式
        self.left_text.tag_configure("removed", background="#ffcccc", foreground="#cc0000")
        self.left_text.tag_configure("modified", background="#ffffcc", foreground="#cc6600")
        self.left_text.tag_configure("same", background="#ffffff")
        
        self.right_text.tag_configure("added", background="#ccffcc", foreground="#006600")
        self.right_text.tag_configure("modified", background="#ffffcc", foreground="#cc6600")
        self.right_text.tag_configure("same", background="#ffffff")
        
        # 清空现有标签
        self.left_text.tag_remove("removed", "1.0", tk.END)
        self.left_text.tag_remove("modified", "1.0", tk.END)
        self.left_text.tag_remove("same", "1.0", tk.END)
        
        self.right_text.tag_remove("added", "1.0", tk.END)
        self.right_text.tag_remove("modified", "1.0", tk.END)
        self.right_text.tag_remove("same", "1.0", tk.END)
        
        # 应用行级标签
        for line_pos in differences['removed']:
            line_num = line_pos + 1
            start = f"{line_num}.0"
            end = f"{line_num}.end"
            self.left_text.tag_add("removed", start, end)
        
        for line_pos in differences['added']:
            line_num = line_pos + 1
            start = f"{line_num}.0"
            end = f"{line_num}.end"
            self.right_text.tag_add("added", start, end)
        
        for line_pos in differences['modified']:
            line_num = line_pos + 1
            start = f"{line_num}.0"
            end = f"{line_num}.end"
            self.left_text.tag_add("modified", start, end)
            self.right_text.tag_add("modified", start, end)
        
        for line_pos in differences['same']:
            line_num = line_pos + 1
            start = f"{line_num}.0"
            end = f"{line_num}.end"
            self.left_text.tag_add("same", start, end)
            self.right_text.tag_add("same", start, end)
    
    
    def clear_highlights(self):
        """清空高亮显示"""
        self.left_text.tag_remove("removed", "1.0", tk.END)
        self.left_text.tag_remove("modified", "1.0", tk.END)
        self.left_text.tag_remove("same", "1.0", tk.END)
        
        self.right_text.tag_remove("added", "1.0", tk.END)
        self.right_text.tag_remove("modified", "1.0", tk.END)
        self.right_text.tag_remove("same", "1.0", tk.END)
    
    def clear_texts(self):
        """清空文本内容"""
        self.left_text.delete("1.0", tk.END)
        self.right_text.delete("1.0", tk.END)
        self.clear_highlights()
        self.compare_stats_label.config(text="")
    
    def load_texts_from_files(self):
        """从文件加载文本"""
        # 加载左侧文本
        file_path = filedialog.askopenfilename(
            title="选择左侧文本文件",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.left_text.delete("1.0", tk.END)
                self.left_text.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
        
        # 加载右侧文本
        file_path = filedialog.askopenfilename(
            title="选择右侧文本文件",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.right_text.delete("1.0", tk.END)
                self.right_text.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
    
    def update_stats(self, differences):
        """更新对比统计信息"""
        text_a = self.left_text.get("1.0", tk.END).rstrip('\n')
        text_b = self.right_text.get("1.0", tk.END).rstrip('\n')
        
        added_count = len(differences['added'])
        removed_count = len(differences['removed'])
        modified_count = len(differences['modified'])
        same_count = len(differences['same'])
        
        # 行级统计
        lines_a = text_a.splitlines()
        lines_b = text_b.splitlines()
        total_a = len(lines_a)
        total_b = len(lines_b)
        
        stats_text = f"📊 对比统计: 文本A({total_a}行) vs 文本B({total_b}行) | 新增:{added_count}行 | 删除:{removed_count}行 | 修改:{modified_count}行 | 相同:{same_count}行"
        self.compare_stats_label.config(text=stats_text)
    
    def set_texts(self, text_a, text_b):
        """设置要对比的文本"""
        if self.window and self.window.winfo_exists():
            self.left_text.delete("1.0", tk.END)
            self.left_text.insert("1.0", text_a)
            self.right_text.delete("1.0", tk.END)
            self.right_text.insert("1.0", text_b)
    
    def is_open(self):
        """检查窗口是否打开"""
        return self.window and self.window.winfo_exists()
