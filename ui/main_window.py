#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面 (优化版)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Callable, Dict, Any

# 导入字幕处理模块
from splitters.subtitle_splitter import SubtitleSplitter
from mergers.subtitle_merger import SubtitleMerger
from ui.text_compare import TextCompareWindow


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("字幕分割工具")
        self.root.geometry("1200x800")
        
        # 设置白色主题
        self.root.configure(bg='#ffffff')
        
        # 设置样式
        self.setup_styles()
        
        # 初始化分割器和合并器
        self.splitter = SubtitleSplitter()
        self.merger = SubtitleMerger()
        
        # 初始化文本对比窗口
        self.text_compare = TextCompareWindow(root)
        
        # 批量处理相关变量
        self.batch_files = []
        self.current_batch_index = 0
        
        # 创建界面
        self.create_widgets()
        
        # 配置网格权重
        self.setup_grid_weights()
        
        # 添加窗口图标和标题栏样式
        self.setup_window_style()
        
        # ==================== 全局滚轮事件绑定 ====================
        # 将滚轮事件绑定到整个应用窗口，这样无论鼠标在哪都能触发滚动
        self.root.bind_all("<MouseWheel>", self.on_canvas_mousewheel)
        self.root.bind_all("<Button-4>", self.on_canvas_mousewheel)  # 适用于Linux向上滚动
        self.root.bind_all("<Button-5>", self.on_canvas_mousewheel)  # 适用于Linux向下滚动
        # ================================================================

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        self.colors = {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8f9fa',
            'bg_tertiary': '#e9ecef',
            'text_primary': '#212529',
            'text_secondary': '#6c757d',
            'accent_blue': '#007bff',
            'accent_green': '#28a745',
            'accent_orange': '#fd7e14',
            'accent_red': '#dc3545',
            'border': '#dee2e6',
            'hover': '#e9ecef'
        }
        
        style.configure('.', background=self.colors['bg_primary'], foreground=self.colors['text_primary'], bordercolor=self.colors['border'])
        style.configure('TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_primary'])
        style.configure('TFrame', background=self.colors['bg_primary'])
        style.configure('TLabelframe', background=self.colors['bg_primary'], bordercolor=self.colors['border'])
        style.configure('TLabelframe.Label', background=self.colors['bg_primary'], foreground=self.colors['text_secondary'])
        
        style.configure('Card.TFrame', background=self.colors['bg_secondary'], relief='raised', borderwidth=1)
        style.configure('InfoCard.TFrame', background=self.colors['bg_secondary'], relief='raised', borderwidth=1)
        
        style.configure('Title.TLabel', font=('Microsoft YaHei', 18, 'bold'), background=self.colors['bg_primary'])
        style.configure('CardTitle.TLabel', font=('Microsoft YaHei', 12, 'bold'), background=self.colors['bg_secondary'])
        style.configure('Info.TLabel', font=('Microsoft YaHei', 10), background=self.colors['bg_secondary'])
        style.configure('InfoSecondary.TLabel', font=('Microsoft YaHei', 9), background=self.colors['bg_secondary'], foreground=self.colors['text_secondary'])
        
        style.configure('Success.TLabel', foreground=self.colors['accent_green'], background=self.colors['bg_secondary'])
        style.configure('Error.TLabel', foreground=self.colors['accent_red'], background=self.colors['bg_secondary'])
        
        # 按钮样式
        btn_padding = (12, 6)
        style.configure('TButton', font=('Microsoft YaHei', 10), padding=btn_padding, borderwidth=1, focusthickness=0)
        style.map('TButton', background=[('active', self.colors['hover'])], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

        style.configure('Primary.TButton', background=self.colors['accent_blue'], foreground='white', borderwidth=0)
        style.configure('Secondary.TButton', background=self.colors['bg_tertiary'], foreground=self.colors['text_primary'])
        style.configure('Success.TButton', background=self.colors['accent_green'], foreground='white', borderwidth=0)
        style.configure('Danger.TButton', background=self.colors['accent_red'], foreground='white', borderwidth=0)
        
        # 输入框样式
        style.configure('TEntry', fieldbackground=self.colors['bg_tertiary'], foreground=self.colors['text_primary'],
                        insertcolor=self.colors['text_primary'], bordercolor=self.colors['border'], padding=5)
        
        # 单选按钮样式
        style.configure('TRadiobutton', background=self.colors['bg_secondary'], foreground=self.colors['text_primary'], font=('Microsoft YaHei', 10))
        style.map('TRadiobutton', background=[('active', self.colors['bg_secondary'])])

        # 进度条样式
        style.configure('Modern.Horizontal.TProgressbar', background=self.colors['accent_blue'], troughcolor=self.colors['bg_tertiary'], borderwidth=0)

        # Treeview 样式
        style.configure("Treeview", background=self.colors['bg_tertiary'], fieldbackground=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], rowheight=25)
        style.configure("Treeview.Heading", background=self.colors['bg_secondary'], font=('Microsoft YaHei', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', self.colors['hover'])])

    def setup_window_style(self):
        """设置窗口样式"""
        try:
            self.root.iconbitmap('icon.ico')
        except tk.TclError:
            pass # 图标文件不存在
        self.center_window()
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_canvas_mousewheel(self, event):
        """处理Canvas上的鼠标滚轮事件"""
        delta = 0
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        elif event.delta:
            delta = -1 * (event.delta // 120)
        
        if delta != 0:
            self.main_canvas.yview_scroll(delta, "units")
    
    def create_scrollable_main_container(self):
        """创建可滚动的主容器"""
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0) # 侧边栏列，固定宽度
        main_frame.columnconfigure(1, weight=1) # 主内容列，自动扩展
        
        self.create_sidebar(main_frame)
        self.create_main_content_area(main_frame)
        
    def create_sidebar(self, parent):
        """创建侧边栏"""
        self.sidebar = ttk.Frame(parent, width=220, style='Card.TFrame')
        self.sidebar.grid(row=0, column=0, sticky="ns", pady=(0, 5))
        self.sidebar.grid_propagate(False) # 防止子控件撑开侧边栏
        
        sidebar_title = ttk.Label(self.sidebar, text="🎬 字幕工具", style='Title.TLabel', background=self.colors['bg_secondary'])
        sidebar_title.pack(pady=15, padx=15, anchor='w')
        
        self.sidebar_buttons = {}
        
        self.sidebar_buttons['split'] = ttk.Button(self.sidebar, text="✂️ 分割字幕", command=lambda: self.switch_function('split'), style='Primary.TButton')
        self.sidebar_buttons['split'].pack(fill='x', pady=5, padx=15)
        
        self.sidebar_buttons['merge'] = ttk.Button(self.sidebar, text="🔗 合并字幕", command=lambda: self.switch_function('merge'), style='Secondary.TButton')
        self.sidebar_buttons['merge'].pack(fill='x', pady=5, padx=15)
        
        
        self.sidebar_buttons['compare'] = ttk.Button(self.sidebar, text="🔍 文本对比", command=self.open_text_compare, style='Secondary.TButton')
        self.sidebar_buttons['compare'].pack(fill='x', pady=5, padx=15)
        
        about_btn = ttk.Button(self.sidebar, text="ℹ️ 关于", command=self.show_about, style='Secondary.TButton')
        about_btn.pack(fill='x', pady=5, padx=15)
        
        # 弹簧, 将下面的控件推到底部
        spacer = ttk.Frame(self.sidebar, style='Card.TFrame')
        spacer.pack(fill='y', expand=True)
        
        self.function_indicator = ttk.Label(self.sidebar, text="当前: 分割字幕", style='InfoSecondary.TLabel')
        self.function_indicator.pack(pady=10, padx=15, anchor='w')

    def on_canvas_configure(self, event):
        """当canvas大小改变时，调整内部frame的宽度"""
        canvas_width = event.width
        self.main_canvas.itemconfig(self.canvas_window_id, width=canvas_width)

    def create_main_content_area(self, parent):
        """创建主内容区域"""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.main_canvas = tk.Canvas(self.content_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        # 滚轮事件已通过全局绑定处理，无需在此处单独绑定

        self.canvas_window_id = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # 绑定canvas大小变化事件，以使内部frame宽度适应canvas
        self.main_canvas.bind('<Configure>', self.on_canvas_configure)
        
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

    def switch_function(self, function_name):
        """切换功能模块"""
        self.current_function = function_name
        
        function_names = {'split': '分割字幕', 'merge': '合并字幕'}
        self.function_indicator.config(text=f"当前: {function_names.get(function_name, '未知功能')}")
        
        for name, button in self.sidebar_buttons.items():
            button.configure(style='Primary.TButton' if name == function_name else 'Secondary.TButton')
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if function_name == 'split':
            self.create_split_interface()
        elif function_name == 'merge':
            self.create_merge_interface()

    def create_split_interface(self):
        """创建分割字幕界面"""
        self.scrollable_frame.columnconfigure(0, weight=3) # 左侧参数区域
        self.scrollable_frame.columnconfigure(1, weight=2) # 右侧预览区域
        self.scrollable_frame.rowconfigure(0, weight=1)

        self.left_panel = ttk.Frame(self.scrollable_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.left_panel.columnconfigure(0, weight=1)

        self.right_panel = ttk.Frame(self.scrollable_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        self.create_left_parameter_panel()
        self.create_right_preview_panel()
        

    def create_left_parameter_panel(self):
        """创建左侧参数面板"""
        self.create_file_selection_area(self.left_panel, 0)
        self.create_batch_files_area(self.left_panel, 1)
        self.create_file_info_area(self.left_panel, 2)
        self.create_method_selection_area(self.left_panel, 3)
        self.create_params_area(self.left_panel, 4)
        self.create_action_buttons(self.left_panel, 5)
        self.create_status_bar(self.left_panel, 6)
        
        self.batch_frame.grid_remove() # 初始隐藏
    
    def create_right_preview_panel(self):
        """创建右侧预览面板"""
        self.create_preview_area(self.right_panel, 0)
        
    def create_widgets(self):
        """创建界面组件"""
        self.create_scrollable_main_container()
        self.switch_function('split')
    
    def create_file_selection_area(self, parent, row):
        """创建文件选择区域"""
        file_frame = ttk.LabelFrame(parent, text="文件选择", padding="12")
        file_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)

        # 拖拽区域
        drop_frame = tk.Frame(file_frame, bg=self.colors['bg_tertiary'], relief='solid', bd=1)
        drop_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        drop_frame.columnconfigure(0, weight=1)

        drop_label = tk.Label(drop_frame, text="📄 拖拽字幕文件到此处", bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], font=('Microsoft YaHei', 11))
        drop_label.pack(pady=(15, 5), padx=10)
        
        format_label = tk.Label(drop_frame, text="或点击下方按钮选择 (支持SRT, ASS)", bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'], font=('Microsoft YaHei', 9))
        format_label.pack(pady=(0, 15), padx=10)
        
        # 按钮区域
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        
        button_group = ttk.Frame(button_frame)
        button_group.grid(row=0, column=0)

        select_btn = ttk.Button(button_group, text="📂 选择文件", command=self.select_file, style='Secondary.TButton')
        select_btn.pack(side='left', padx=(0, 5))
        
        batch_btn = ttk.Button(button_group, text="📁 批量选择", command=self.select_batch_files, style='Primary.TButton')
        batch_btn.pack(side='left', padx=5)
        
        
        clear_files_btn = ttk.Button(button_group, text="🗑️ 清空", command=self.clear_files, style='Danger.TButton')
        clear_files_btn.pack(side='left', padx=(5, 0))
        
        # 文件信息显示区域
        self.file_info_frame = ttk.Frame(file_frame)
        self.file_info_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.file_info_frame.columnconfigure(1, weight=1)
        
        self.file_label = ttk.Label(self.file_info_frame, text="未选择文件", wraplength=400, foreground=self.colors['text_secondary'])
        self.file_label.grid(row=0, column=0, sticky='w')
        
        self.batch_count_label = ttk.Label(self.file_info_frame, text="", foreground=self.colors['text_secondary'])
        self.batch_count_label.grid(row=0, column=1, sticky='e')
        
        # 添加文件统计信息标签
        self.batch_stats_label = ttk.Label(self.file_info_frame, text="", foreground=self.colors['text_secondary'])
        self.batch_stats_label.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(5, 0))

    def create_batch_files_area(self, parent, row):
        """创建批量文件列表区域"""
        self.batch_frame = ttk.LabelFrame(parent, text="批量文件列表", padding="15")
        self.batch_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.batch_frame.columnconfigure(0, weight=1)

        list_container = ttk.Frame(self.batch_frame)
        list_container.grid(row=0, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        
        self.batch_tree = ttk.Treeview(list_container, columns=('序号', '文件名', '格式', '行数', '状态'), show='headings', height=5)
        self.batch_tree.heading('序号', text='#'); self.batch_tree.column('序号', width=40, anchor='center', stretch=False)
        self.batch_tree.heading('文件名', text='文件名'); self.batch_tree.column('文件名', width=250, anchor='w')
        self.batch_tree.heading('格式', text='格式'); self.batch_tree.column('格式', width=60, anchor='center', stretch=False)
        self.batch_tree.heading('行数', text='行数'); self.batch_tree.column('行数', width=60, anchor='center', stretch=False)
        self.batch_tree.heading('状态', text='状态'); self.batch_tree.column('状态', width=80, anchor='center', stretch=False)

        batch_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.batch_tree.yview)
        self.batch_tree.configure(yscrollcommand=batch_scrollbar.set)
        
        self.batch_tree.grid(row=0, column=0, sticky="nsew")
        batch_scrollbar.grid(row=0, column=1, sticky="ns")

        batch_ops_frame = ttk.Frame(self.batch_frame)
        batch_ops_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        batch_ops_frame.columnconfigure(0, weight=1)
        
        batch_ops_group = ttk.Frame(batch_ops_frame)
        batch_ops_group.grid(row=0, column=0)
        
        ttk.Button(batch_ops_group, text="⚡ 批量执行", command=self.batch_execute, style='Success.TButton').pack(side='left', padx=5)
        ttk.Button(batch_ops_group, text="⏹️ 停止", command=self.stop_batch, style='Danger.TButton').pack(side='left', padx=5)
        ttk.Button(batch_ops_group, text="📊 预览", command=self.preview_batch, style='Info.TButton').pack(side='left', padx=5)
    
    def create_file_info_area(self, parent, row):
        """创建文件信息显示区域"""
        self.info_frame = ttk.LabelFrame(parent, text="文件信息", padding="12")
        self.info_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.info_frame.columnconfigure(0, weight=1)
        
        self.info_labels = {}
        
        info_cards_data = [
            ('filename', '📄 文件名', '--'), ('format', '🎭 格式', '--'), ('total_count', '📈 行数', '--'),
            ('duration', '⏱️ 时长', '--'), ('time_range', '🕐 时间范围', '--'), ('file_size', '💾 大小', '--')
        ]

        grid_frame = ttk.Frame(self.info_frame)
        grid_frame.grid(row=0, column=0, sticky='ew')
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1, uniform="info_card")

        for i, (key, title, default_value) in enumerate(info_cards_data):
            row_idx, col_idx = divmod(i, 3)
            
            card = ttk.Frame(grid_frame, style='Card.TFrame', padding=8)
            card.grid(row=row_idx, column=col_idx, padx=(0, 5 if col_idx < 2 else 0), pady=(0, 5), sticky='nsew')
            
            ttk.Label(card, text=title, style='InfoSecondary.TLabel').pack(anchor='w')
            value_label = ttk.Label(card, text=default_value, style='Info.TLabel', wraplength=150)
            value_label.pack(anchor='w', pady=(3, 0))
            self.info_labels[key] = value_label
    
    def create_method_selection_area(self, parent, row):
        """创建分割方式选择区域"""
        self.method_frame = ttk.LabelFrame(parent, text="分割方式", padding="12")
        self.method_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.method_var = tk.StringVar()

    def create_params_area(self, parent, row):
        """创建参数设置区域"""
        self.params_frame = ttk.LabelFrame(parent, text="参数设置", padding="12")
        self.params_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        
        self.start_index_var = tk.StringVar()
        self.end_index_var = tk.StringVar()
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.dialog_count_var = tk.StringVar()
        self.split_count_var = tk.StringVar()
    
    def create_preview_area(self, parent, row):
        """创建预览区域"""
        self.preview_frame = ttk.LabelFrame(parent, text="分割预览", padding="12")
        self.preview_frame.grid(row=row, column=0, sticky="nsew")
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)
        
        preview_container = ttk.Frame(self.preview_frame)
        preview_container.grid(row=0, column=0, sticky="nsew")
        preview_container.columnconfigure(0, weight=1)
        preview_container.rowconfigure(0, weight=1)

        self.preview_tree = ttk.Treeview(preview_container, columns=('#', '范围', '时间范围', '行数', '有效'), show='headings')
        self.preview_tree.heading('#', text='#'); self.preview_tree.column('#', width=40, anchor='center', stretch=False)
        self.preview_tree.heading('范围', text='范围'); self.preview_tree.column('范围', width=120, anchor='w')
        self.preview_tree.heading('时间范围', text='时间范围'); self.preview_tree.column('时间范围', width=150, anchor='w')
        self.preview_tree.heading('行数', text='行数'); self.preview_tree.column('行数', width=60, anchor='center', stretch=False)
        self.preview_tree.heading('有效', text='有效'); self.preview_tree.column('有效', width=60, anchor='center', stretch=False)
        
        preview_scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        preview_scrollbar.grid(row=0, column=1, sticky="ns")

    def create_action_buttons(self, parent, row):
        """创建操作按钮区域"""
        self.action_button_frame = ttk.Frame(parent)
        self.action_button_frame.grid(row=row, column=0, pady=(0, 10))
        
        self.preview_button = ttk.Button(self.action_button_frame, text="🔍 预览分割", command=self.preview_split, style='Secondary.TButton')
        self.preview_button.pack(side='left', padx=(0, 10))
        
        self.execute_button = ttk.Button(self.action_button_frame, text="⚡ 执行分割", command=self.execute_split, style='Success.TButton')
        self.execute_button.pack(side='left')
    
    def update_action_buttons_visibility(self):
        """根据当前模式更新操作按钮的显示状态"""
        if len(self.batch_files) > 1:
            # 批量模式：隐藏单文件操作按钮
            self.preview_button.pack_forget()
            self.execute_button.pack_forget()
        elif len(self.batch_files) == 1:
            # 单文件模式：显示单文件操作按钮
            self.preview_button.pack(side='left', padx=(0, 10))
            self.execute_button.pack(side='left')
        else:
            # 无文件模式：隐藏按钮
            self.preview_button.pack_forget()
            self.execute_button.pack_forget()

    def create_status_bar(self, parent, row):
        """创建状态栏"""
        self.status_frame = ttk.LabelFrame(parent, text="状态", padding=10)
        self.status_frame.grid(row=row, column=0, sticky="ew", pady=(10, 0))
        self.status_frame.columnconfigure(0, weight=1)
        
        status_info_frame = ttk.Frame(self.status_frame)
        status_info_frame.grid(row=0, column=0, sticky="ew")
        status_info_frame.columnconfigure(1, weight=1)
        
        self.status_indicator = ttk.Label(status_info_frame, text="🟢")
        self.status_indicator.grid(row=0, column=0, padx=(0, 8))
        
        self.status_label = ttk.Label(status_info_frame, text="就绪")
        self.status_label.grid(row=0, column=1, sticky="w")
        
        self.version_label = ttk.Label(status_info_frame, text="v2.0", foreground=self.colors['text_secondary'])
        self.version_label.grid(row=0, column=2, sticky="e")
        
        self.progress = ttk.Progressbar(self.status_frame, mode='determinate', style='Modern.Horizontal.TProgressbar')
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.progress.grid_remove()

    def setup_grid_weights(self):
        """配置网格权重"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def select_file(self):
        """选择单个字幕文件"""
        file_path = filedialog.askopenfilename(filetypes=[("Subtitle Files", "*.srt *.ass"), ("All files", "*.*")])
        if file_path:
            self.batch_files = [file_path]
            self.current_batch_index = 0
            self.load_current_file()
            self.batch_frame.grid_remove()
            self.batch_count_label.config(text="")
            self.update_action_buttons_visibility()

    def select_batch_files(self):
        """批量选择字幕文件"""
        file_paths = filedialog.askopenfilenames(filetypes=[("Subtitle Files", "*.srt *.ass"), ("All files", "*.*")])
        if file_paths:
            self.batch_files = list(file_paths)
            self.current_batch_index = 0
            self.update_batch_files_display()
            self.load_current_file()
            self.batch_frame.grid()
            self.update_status(f"已选择 {len(self.batch_files)} 个文件")
            self.update_action_buttons_visibility()
    
    def clear_files(self):
        """清空文件列表"""
        self.batch_files = []
        self.current_batch_index = 0
        self.splitter = SubtitleSplitter() # 重置分割器
        self.update_batch_files_display()
        self.file_label.config(text="未选择文件")
        self.batch_count_label.config(text="")
        self.batch_frame.grid_remove()
        self.clear_all()
        self.update_status("已清空文件列表")
        self.update_action_buttons_visibility()
    
    def update_batch_files_display(self):
        """更新批量文件列表显示"""
        self.batch_tree.delete(*self.batch_tree.get_children())
        if not self.batch_files:
            self.batch_count_label.config(text="")
            return

        # 异步获取文件信息，避免界面卡顿
        self.root.after(100, self._load_batch_files_info)
        
        # 先显示基本信息
        for i, file_path in enumerate(self.batch_files):
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].upper().replace('.', '')
            self.batch_tree.insert('', 'end', values=(i + 1, filename, ext, "加载中...", "就绪"))
        
        self.batch_count_label.config(text=f"共 {len(self.batch_files)} 个文件")
    
    def _load_batch_files_info(self):
        """异步加载批量文件信息"""
        total_lines_all = 0
        total_size_all = 0
        min_lines = float('inf')
        max_lines = 0
        error_count = 0
        
        for i, file_path in enumerate(self.batch_files):
            try:
                # 获取文件行数
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines = len(f.readlines())
                
                # 获取文件大小
                file_size = os.path.getsize(file_path)
                file_size_kb = file_size / 1024
                
                # 更新显示
                if i < len(self.batch_tree.get_children()):
                    item_id = self.batch_tree.get_children()[i]
                    self.batch_tree.set(item_id, '行数', f"{total_lines}行")
                
                # 统计信息
                total_lines_all += total_lines
                total_size_all += file_size
                min_lines = min(min_lines, total_lines)
                max_lines = max(max_lines, total_lines)
                
                # 更新状态
                self.update_status(f"已加载文件信息: {os.path.basename(file_path)} ({total_lines}行)", "success")
                
            except Exception as e:
                error_count += 1
                if i < len(self.batch_tree.get_children()):
                    item_id = self.batch_tree.get_children()[i]
                    self.batch_tree.set(item_id, '行数', "错误")
                    self.batch_tree.set(item_id, '状态', "❌ 错误")
            
            # 更新界面
            self.root.update_idletasks()
        
        # 更新统计信息显示
        self._update_batch_stats(total_lines_all, total_size_all, min_lines, max_lines, error_count)
    
    def _update_batch_stats(self, total_lines, total_size, min_lines, max_lines, error_count):
        """更新批量文件统计信息"""
        if error_count > 0:
            stats_text = f"⚠️ {error_count} 个文件加载失败"
        else:
            avg_lines = total_lines // len(self.batch_files) if self.batch_files else 0
            total_size_mb = total_size / (1024 * 1024)
            
            if min_lines == max_lines:
                stats_text = f"📊 所有文件行数一致: {min_lines}行 | 总大小: {total_size_mb:.1f}MB"
            else:
                stats_text = f"📊 行数范围: {min_lines}-{max_lines}行 | 平均: {avg_lines}行 | 总计: {total_lines}行 | 总大小: {total_size_mb:.1f}MB"
        
        self.batch_stats_label.config(text=stats_text)
    
    def load_current_file(self):
        """加载当前选中的文件"""
        if not self.batch_files:
            self.clear_all()
            return
        
        current_file = self.batch_files[self.current_batch_index]
        self.update_status(f"加载中: {os.path.basename(current_file)}")
        
        if self.splitter.load_file(current_file):
            self.file_label.config(text=os.path.basename(current_file))
            self.display_file_info()
            self.update_method_options()
            self.update_status(f"加载成功: {os.path.basename(current_file)}", "success")
            
            if len(self.batch_files) > 1:
                info = self.splitter.get_file_info()
                self.update_batch_file_info(self.current_batch_index, info.get('total_count', 0))
        else:
            messagebox.showerror("错误", f"文件加载失败: {os.path.basename(current_file)}")
            self.update_status("文件加载失败", "error")
    
    def update_batch_file_info(self, index, total_lines):
        """更新批量文件列表中的文件信息"""
        if index < len(self.batch_tree.get_children()):
            item_id = self.batch_tree.get_children()[index]
            self.batch_tree.set(item_id, '行数', f"{total_lines}行")

    def display_file_info(self):
        """显示文件信息"""
        info = self.splitter.get_file_info()
        self.info_labels['filename'].config(text=info.get('filename', '--'))
        self.info_labels['format'].config(text=info.get('format', '--'))
        self.info_labels['total_count'].config(text=f"{info.get('total_count', 0)} 行")
        
        duration_s = info.get('duration_seconds', 0)
        duration_txt = f"{int(duration_s//3600):02d}:{int((duration_s%3600)//60):02d}:{int(duration_s%60):02d}" if duration_s > 0 else "--"
        self.info_labels['duration'].config(text=duration_txt)
        
        self.info_labels['time_range'].config(text=f"{info.get('start_time', '--')} -> {info.get('end_time', '--')}")
        
        file_size_kb = info.get('file_size', 0) / 1024
        self.info_labels['file_size'].config(text=f"{file_size_kb:.1f} KB" if file_size_kb > 0 else "--")
    
    def update_method_options(self):
        """更新分割方式选项"""
        for widget in self.method_frame.winfo_children():
            widget.destroy()
        
        file_format = self.splitter.file_format
        options = []
        if file_format in ['SRT', 'ASS']:
            options = [("按文件行数分割", "line_split")]
        
        for text, value in options:
            ttk.Radiobutton(self.method_frame, text=text, variable=self.method_var, value=value, command=self.update_params_ui).pack(anchor='w', pady=2)
        
        if options:
            self.method_var.set(options[0][1])
            self.update_params_ui()
    
    def update_params_ui(self):
        """更新参数输入界面"""
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        method = self.method_var.get()
        if method == "line_split": self.create_line_split_params()

    def _create_param_entry(self, parent, label_text, textvariable, row, col):
        ttk.Label(parent, text=label_text).grid(row=row, column=col, padx=(0, 5), sticky='w')
        ttk.Entry(parent, textvariable=textvariable, width=12).grid(row=row, column=col + 1, sticky="ew")

    def create_line_split_params(self):
        """创建按文件行数分割的参数界面"""
        container = ttk.Frame(self.params_frame); container.pack(fill='x')
        
        # 模式选择区域
        mode_frame = ttk.LabelFrame(container, text="批量处理模式", padding="10")
        mode_frame.pack(fill='x', pady=(0, 10))
        
        # 模式选择变量
        self.batch_mode_var = tk.StringVar(value="uniform")
        
        # 统一模式
        uniform_frame = ttk.Frame(mode_frame)
        uniform_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Radiobutton(uniform_frame, text="统一模式 - 所有文件使用相同参数", 
                       variable=self.batch_mode_var, value="uniform", 
                       command=self.update_mode_params).pack(anchor='w')
        
        self.uniform_params_frame = ttk.Frame(uniform_frame)
        self.uniform_params_frame.pack(fill='x', padx=(20, 0), pady=(5, 0))
        
        # 智能模式
        smart_frame = ttk.Frame(mode_frame)
        smart_frame.pack(fill='x')
        
        ttk.Radiobutton(smart_frame, text="智能模式 - 根据文件行数自动计算参数", 
                       variable=self.batch_mode_var, value="smart", 
                       command=self.update_mode_params).pack(anchor='w')
        
        self.smart_params_frame = ttk.Frame(smart_frame)
        self.smart_params_frame.pack(fill='x', padx=(20, 0), pady=(5, 0))
        
        # 初始化参数
        self.dialog_count_var.set("100"); self.split_count_var.set("5")
        self.update_mode_params()
    
    def update_mode_params(self):
        """更新模式参数界面"""
        # 清除现有参数界面
        for widget in self.uniform_params_frame.winfo_children():
            widget.destroy()
        for widget in self.smart_params_frame.winfo_children():
            widget.destroy()
        
        mode = self.batch_mode_var.get()
        
        if mode == "uniform":
            # 统一模式参数
            for i in range(4): self.uniform_params_frame.columnconfigure(i, weight=1, uniform='a')
            self._create_param_entry(self.uniform_params_frame, "每文件行数:", self.dialog_count_var, 0, 0)
            self._create_param_entry(self.uniform_params_frame, "分割数量:", self.split_count_var, 0, 2)
        elif mode == "smart":
            # 智能模式参数
            for i in range(4): self.smart_params_frame.columnconfigure(i, weight=1, uniform='a')
            self._create_param_entry(self.smart_params_frame, "目标分割数:", self.split_count_var, 0, 0)
            
            # 添加说明标签
            info_label = ttk.Label(self.smart_params_frame, 
                                 text="系统将根据每个文件的行数自动计算每份应包含的行数", 
                                 foreground='gray', font=('Arial', 9))
            info_label.grid(row=1, column=0, columnspan=4, sticky='w', pady=(5, 0))
    
    def _get_params(self):
        """获取当前UI上的参数并验证"""
        method = self.method_var.get()
        params = {'method': method}
        try:
            if method == "line_split":
                batch_mode = self.batch_mode_var.get()
                params.update({
                    'batch_mode': batch_mode,
                    'split_count': int(self.split_count_var.get())
                })
                
                # 只有在统一模式下才需要lines_per_split参数
                if batch_mode == "uniform":
                    params['lines_per_split'] = int(self.dialog_count_var.get())
                else:
                    # 智能模式下，lines_per_split会在分割器中自动计算
                    params['lines_per_split'] = 0  # 占位符，实际不会被使用
                    
            return params
        except ValueError:
            raise ValueError("参数无效，请输入正确的数字。")

    def preview_split(self):
        """预览分割结果"""
        if not self.splitter.current_file: return messagebox.showwarning("警告", "请先选择字幕文件")
        try:
            params = self._get_params()
            self.update_status("正在生成预览...", "loading")
            preview_data = self.splitter.preview_split(**params)
            self.display_preview(preview_data)
            self.update_status("预览生成完成", "success")
        except Exception as e:
            messagebox.showerror("错误", str(e)); self.update_status("预览失败", "error")

    def display_preview(self, preview_data):
        """显示预览结果"""
        self.preview_tree.delete(*self.preview_tree.get_children())
        if not preview_data:
            self.preview_tree.insert('', 'end', values=('-', '没有可预览的分割结果', '-', '-', '-'))
        else:
            for item in preview_data:
                icon = "✅" if item['count'] > 0 else "❌"
                self.preview_tree.insert('', 'end', values=(item['split_num'], item['range'], item['time_range'], f"{item['count']}行", icon))
    
    def execute_split(self):
        """执行分割操作"""
        if not self.splitter.current_file: return messagebox.showwarning("警告", "请先选择字幕文件")
        try:
            params = self._get_params()
            self.update_status("正在执行分割...", "loading"); self.show_progress(True)
            
            func_map = {
                "line_split": self.splitter.split_by_lines
            }
            # 移除method参数，因为分割方法不需要它
            method = params.pop('method')
            batch_mode = params.pop('batch_mode', 'uniform')
            saved_files = func_map[method](**params, batch_mode=batch_mode)
            
            if saved_files:
                messagebox.showinfo("成功", f"字幕分割完成！\n生成了 {len(saved_files)} 个文件。")
                self.update_status(f"分割完成，生成 {len(saved_files)} 个文件", "success")
            else:
                messagebox.showwarning("警告", "没有生成任何分割文件。")
                self.update_status("分割未生成文件", "warning")
        except Exception as e:
            messagebox.showerror("错误", str(e)); self.update_status("分割失败", "error")
        finally:
            self.show_progress(False)

    def clear_all(self):
        """清空参数、选项和预览，保留文件信息"""
        for widget in self.method_frame.winfo_children(): widget.destroy()
        for widget in self.params_frame.winfo_children(): widget.destroy()
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        if self.splitter.current_file:
            self.display_file_info()
            self.update_method_options()
        else:
             for label in self.info_labels.values(): label.config(text="--")

        self.update_status("已清空参数和预览")
    
    def batch_execute(self):
        """批量执行分割操作"""
        if len(self.batch_files) <= 1: return messagebox.showwarning("警告", "请先使用“批量选择”选择多个文件。")
        if not messagebox.askyesno("确认", f"确定要对 {len(self.batch_files)} 个文件执行批量分割吗？"): return
        
        try:
            params = self._get_params()
            self.show_progress(True, 0)
            success_count, total_saved_files, failed_files = 0, 0, []

            for i, file_path in enumerate(self.batch_files):
                self.current_batch_index = i
                self.update_batch_file_status(i, "🔄 处理中")
                progress_percent = (i / len(self.batch_files)) * 100
                self.progress['value'] = progress_percent
                self.update_status(f"处理中 {i+1}/{len(self.batch_files)}: {os.path.basename(file_path)} ({progress_percent:.1f}%)", "loading")
                
                if not self.splitter.load_file(file_path):
                    failed_files.append(f"{os.path.basename(file_path)}: 加载失败"); self.update_batch_file_status(i, "❌ 失败"); continue
                
                try:
                    func_map = {"line_split": self.splitter.split_by_lines}
                    # 移除method参数，因为分割方法不需要它
                    method = params['method']
                    params_copy = params.copy()
                    batch_mode = params_copy.pop('batch_mode', 'uniform')
                    params_copy.pop('method')
                    saved_files = func_map[method](**params_copy, batch_mode=batch_mode)
                    
                    if saved_files:
                        total_saved_files += len(saved_files); success_count += 1
                        self.update_batch_file_status(i, "✅ 完成")
                    else:
                        failed_files.append(f"{os.path.basename(file_path)}: 未生成文件"); self.update_batch_file_status(i, "⚠️ 警告")
                except Exception as e:
                    failed_files.append(f"{os.path.basename(file_path)}: {e}"); self.update_batch_file_status(i, "❌ 错误")
                self.root.update_idletasks()
            
            self.progress['value'] = 100
            self.update_status(f"批量处理完成！成功: {success_count}, 失败: {len(failed_files)}", "success")
            
            msg = f"批量分割完成！\n\n✅ 成功处理: {success_count} 文件\n📁 共生成: {total_saved_files} 文件"
            if failed_files:
                msg += f"\n\n❌ 失败: {len(failed_files)} 文件\n详情:\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5: msg += f"\n...等 {len(failed_files) - 5} 个文件"
            messagebox.showinfo("批量处理完成", msg)
        except Exception as e:
            messagebox.showerror("错误", str(e)); self.update_status("批量处理失败", "error")
        finally:
            self.show_progress(False)
    
    def update_batch_file_status(self, index, status):
        if index < len(self.batch_tree.get_children()):
            item_id = self.batch_tree.get_children()[index]
            self.batch_tree.set(item_id, '状态', status)
    
    def preview_batch(self):
        """预览批量处理结果"""
        if len(self.batch_files) <= 1:
            messagebox.showwarning("警告", "请先使用'批量选择'选择多个文件。")
            return
        
        try:
            params = self._get_params()
            preview_data = []
            
            for i, file_path in enumerate(self.batch_files):
                if not self.splitter.load_file(file_path):
                    continue
                
                # 获取文件信息
                info = self.splitter.get_file_info()
                total_lines = info.get('total_count', 0)
                
                # 计算分割预览
                lines_per_split = params.get('lines_per_split', 100)
                split_count = params.get('split_count', 5)
                batch_mode = params.get('batch_mode', 'uniform')
                
                if batch_mode == "smart":
                    # 智能模式：根据文件行数自动计算
                    lines_per_split = total_lines // split_count
                    if lines_per_split == 0:
                        lines_per_split = 1
                    actual_split_count = split_count
                else:
                    # 统一模式：使用用户指定的行数
                    actual_split_count = min(split_count, (total_lines + lines_per_split - 1) // lines_per_split)
                
                file_preview = {
                    'file_name': os.path.basename(file_path),
                    'total_lines': total_lines,
                    'split_count': actual_split_count,
                    'lines_per_split': lines_per_split
                }
                preview_data.append(file_preview)
            
            # 显示预览窗口
            self._show_batch_preview(preview_data, params)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def _show_batch_preview(self, preview_data, params):
        """显示批量处理预览窗口"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("批量处理预览")
        preview_window.geometry("800x600")
        preview_window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(preview_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="批量处理预览", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 参数信息
        params_frame = ttk.LabelFrame(main_frame, text="处理参数", padding="10")
        params_frame.pack(fill='x', pady=(0, 10))
        
        batch_mode = params.get('batch_mode', 'uniform')
        if batch_mode == "smart":
            params_text = f"模式: 智能模式\n目标分割数: {params.get('split_count', 5)}个\n系统将自动计算每份行数"
        else:
            params_text = f"模式: 统一模式\n每文件行数: {params.get('lines_per_split', 100)}行\n分割数量: {params.get('split_count', 5)}个"
        ttk.Label(params_frame, text=params_text).pack(anchor='w')
        
        # 文件列表
        files_frame = ttk.LabelFrame(main_frame, text="文件处理预览", padding="10")
        files_frame.pack(fill='both', expand=True)
        
        # 创建表格
        columns = ('文件名', '总行数', '分割数', '每份行数', '状态')
        tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        
        # 添加数据
        total_files = len(preview_data)
        total_splits = 0
        
        for data in preview_data:
            status = "✅ 正常" if data['total_lines'] > 0 else "❌ 错误"
            tree.insert('', 'end', values=(
                data['file_name'],
                f"{data['total_lines']}行",
                f"{data['split_count']}个",
                f"{data['lines_per_split']}行",
                status
            ))
            total_splits += data['split_count']
        
        tree.pack(fill='both', expand=True)
        
        # 统计信息
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=(10, 0))
        
        stats_text = f"📊 统计信息: 共{total_files}个文件，预计生成{total_splits}个分割文件"
        ttk.Label(stats_frame, text=stats_text, font=('Arial', 10, 'bold')).pack()
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="开始处理", command=lambda: [preview_window.destroy(), self.batch_execute()]).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=preview_window.destroy).pack(side='right')
    
    def stop_batch(self):
        """停止批量处理"""
        # 实际停止需要更复杂的线程管理，此处为UI重置
        self.update_status("批量处理已停止", "warning")
        self.show_progress(False)
    
    def open_text_compare(self):
        """打开文本对比窗口"""
        self.text_compare.open()
    
    
    def show_about(self):
        messagebox.showinfo("关于 字幕分割工具",
                            "一个使用Python和tkinter构建的现代GUI工具，用于分割SRT和ASS字幕文件。\n\n"
                            "开发者:B站阿狗BIGP\n版本: 1.0")
    
    def update_status(self, message: str, status_type: str = "info"):
        self.status_label.config(text=message)
        status_map = {"success": "🟢", "error": "🔴", "warning": "🟡", "loading": "🔄"}
        self.status_indicator.config(text=status_map.get(status_type, "🟢"))
        self.root.update_idletasks()
    
    def show_progress(self, show: bool, value=0):
        if show:
            self.progress.grid(); self.progress['value'] = value
        else:
            self.progress.grid_remove()
    
    def create_merge_interface(self):
        """创建合并字幕界面"""
        self.scrollable_frame.columnconfigure(0, weight=3)  # 左侧参数区域
        self.scrollable_frame.columnconfigure(1, weight=2)  # 右侧预览区域
        
        # 创建左右面板
        self.create_merge_layout()
    
    def create_merge_layout(self):
        """创建合并布局"""
        # 左侧参数面板
        self.left_panel = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        self.left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        self.left_panel.columnconfigure(0, weight=1)
        
        # 右侧预览面板
        self.right_panel = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        self.right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)
        
        # 创建左侧参数区域
        self.create_merge_parameter_panel()
        
        # 创建右侧预览区域
        self.create_merge_preview_panel()
    
    def create_merge_parameter_panel(self):
        """创建合并参数面板"""
        # 文件选择区域
        self.create_merge_file_selection_area()
        
        # 文件列表区域
        self.create_merge_file_list_area()
        
        # 输出设置区域
        self.create_merge_output_settings_area()
        
        # 操作按钮区域
        self.create_merge_action_buttons()
        
        # 状态栏
        self.create_merge_status_bar()
    
    def create_merge_file_selection_area(self):
        """创建合并文件选择区域"""
        file_frame = ttk.LabelFrame(self.left_panel, text="📁 选择要合并的文件", padding="12")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        file_frame.columnconfigure(0, weight=1)
        
        # 按钮区域
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        
        ttk.Button(btn_frame, text="📂 添加文件", command=self.add_merge_files, style='Primary.TButton').grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="🗑️ 清空列表", command=self.clear_merge_files, style='Danger.TButton').grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="⬆️ 上移", command=self.move_merge_file_up, style='Secondary.TButton').grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 文件信息显示
        self.merge_file_info_frame = ttk.Frame(file_frame)
        self.merge_file_info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.merge_file_info_frame.columnconfigure(0, weight=1)
        
        self.merge_file_count_label = ttk.Label(self.merge_file_info_frame, text="已选择: 0 个文件", style='Info.TLabel')
        self.merge_file_count_label.grid(row=0, column=0, sticky=tk.W)
    
    def create_merge_file_list_area(self):
        """创建合并文件列表区域"""
        list_frame = ttk.LabelFrame(self.left_panel, text="📋 文件列表 (按合并顺序)", padding="12")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('#', '文件名', '格式', '行数', '时长')
        self.merge_file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题和宽度
        self.merge_file_tree.heading('#', text='#')
        self.merge_file_tree.heading('文件名', text='文件名')
        self.merge_file_tree.heading('格式', text='格式')
        self.merge_file_tree.heading('行数', text='行数')
        self.merge_file_tree.heading('时长', text='时长')
        
        self.merge_file_tree.column('#', width=40)
        self.merge_file_tree.column('文件名', width=200)
        self.merge_file_tree.column('格式', width=60)
        self.merge_file_tree.column('行数', width=60)
        self.merge_file_tree.column('时长', width=80)
        
        # 滚动条
        merge_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.merge_file_tree.yview)
        self.merge_file_tree.configure(yscrollcommand=merge_scrollbar.set)
        
        # 布局
        self.merge_file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        merge_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定选择事件
        self.merge_file_tree.bind('<<TreeviewSelect>>', self.on_merge_file_select)
    
    def create_merge_output_settings_area(self):
        """创建合并输出设置区域"""
        output_frame = ttk.LabelFrame(self.left_panel, text="⚙️ 输出设置", padding="12")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        output_frame.columnconfigure(1, weight=1)
        
        # 输出文件名
        ttk.Label(output_frame, text="输出文件名:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.merge_output_name_var = tk.StringVar(value="merged_subtitles")
        ttk.Entry(output_frame, textvariable=self.merge_output_name_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 输出格式
        ttk.Label(output_frame, text="输出格式:", style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.merge_output_format_var = tk.StringVar(value="自动检测")
        format_combo = ttk.Combobox(output_frame, textvariable=self.merge_output_format_var, 
                                   values=["自动检测", "SRT", "ASS"], state="readonly")
        format_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 输出目录
        ttk.Label(output_frame, text="输出目录:", style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(output_frame)
        dir_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        dir_frame.columnconfigure(0, weight=1)
        
        self.merge_output_dir_var = tk.StringVar(value=os.getcwd())
        ttk.Entry(dir_frame, textvariable=self.merge_output_dir_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="📁", command=self.select_merge_output_dir, style='Secondary.TButton').grid(row=0, column=1)
    
    def create_merge_action_buttons(self):
        """创建合并操作按钮"""
        button_frame = ttk.Frame(self.left_panel)
        button_frame.grid(row=3, column=0, pady=(0, 15))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="🔍 预览合并", command=self.preview_merge, style='Secondary.TButton').grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="🚀 开始合并", command=self.start_merge, style='Success.TButton').grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
    
    def create_merge_status_bar(self):
        """创建合并状态栏"""
        self.merge_status_frame = ttk.Frame(self.left_panel)
        self.merge_status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.merge_status_frame.columnconfigure(1, weight=1)
        
        self.merge_status_indicator = ttk.Label(self.merge_status_frame, text="🟢", style='Info.TLabel')
        self.merge_status_indicator.grid(row=0, column=0, padx=(0, 5))
        
        self.merge_status_label = ttk.Label(self.merge_status_frame, text="准备就绪", style='Info.TLabel')
        self.merge_status_label.grid(row=0, column=1, sticky=tk.W)
        
        self.merge_progress = ttk.Progressbar(self.merge_status_frame, mode='determinate')
        self.merge_progress.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.merge_progress.grid_remove()
    
    def create_merge_preview_panel(self):
        """创建合并预览面板"""
        preview_frame = ttk.LabelFrame(self.right_panel, text="👁️ 合并预览", padding="12")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # 预览信息
        self.merge_preview_text = tk.Text(preview_frame, height=20, wrap=tk.WORD, 
                                         bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                                         font=('Consolas', 10))
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.merge_preview_text.yview)
        self.merge_preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.merge_preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 初始化预览内容
        self.merge_preview_text.insert(tk.END, "请选择要合并的字幕文件...")
    
    # 合并功能相关方法
    def add_merge_files(self):
        """添加要合并的文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择要合并的字幕文件",
            filetypes=[("字幕文件", "*.srt *.ass"), ("SRT文件", "*.srt"), ("ASS文件", "*.ass"), ("所有文件", "*.*")]
        )
        
        if file_paths:
            if not hasattr(self, 'merge_files'):
                self.merge_files = []
            
            for file_path in file_paths:
                if file_path not in self.merge_files:
                    self.merge_files.append(file_path)
            
            self.update_merge_file_display()
    
    def clear_merge_files(self):
        """清空合并文件列表"""
        if hasattr(self, 'merge_files'):
            self.merge_files = []
            self.update_merge_file_display()
    
    def update_merge_file_display(self):
        """更新合并文件显示"""
        if not hasattr(self, 'merge_files'):
            self.merge_files = []
        
        # 清空现有项目
        for item in self.merge_file_tree.get_children():
            self.merge_file_tree.delete(item)
        
        # 添加文件信息
        for i, file_path in enumerate(self.merge_files):
            file_info = self.merger.get_file_info(file_path)
            if 'error' not in file_info:
                self.merge_file_tree.insert('', 'end', values=(
                    i + 1,
                    os.path.basename(file_path),
                    file_info.get('format', '--'),
                    file_info.get('count', '--'),
                    file_info.get('duration', '--')
                ))
        
        # 更新文件计数
        self.merge_file_count_label.config(text=f"已选择: {len(self.merge_files)} 个文件")
    
    def move_merge_file_up(self):
        """上移选中的文件"""
        selection = self.merge_file_tree.selection()
        if not selection or not hasattr(self, 'merge_files'):
            return
        
        selected_index = self.merge_file_tree.index(selection[0])
        if selected_index > 0:
            # 交换文件位置
            self.merge_files[selected_index], self.merge_files[selected_index - 1] = \
                self.merge_files[selected_index - 1], self.merge_files[selected_index]
            
            # 更新显示
            self.update_merge_file_display()
            # 重新选中移动后的文件
            self.merge_file_tree.selection_set(self.merge_file_tree.get_children()[selected_index - 1])
    
    def on_merge_file_select(self, event):
        """合并文件选择事件"""
        selection = self.merge_file_tree.selection()
        if selection:
            # 可以在这里添加文件详细信息显示
            pass
    
    def select_merge_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.merge_output_dir_var.set(directory)
    
    def preview_merge(self):
        """预览合并结果"""
        if not hasattr(self, 'merge_files') or not self.merge_files:
            messagebox.showwarning("警告", "请先选择要合并的文件")
            return
        
        # 清空预览
        self.merge_preview_text.delete(1.0, tk.END)
        
        # 显示合并信息
        preview_text = "=== 合并预览 ===\n\n"
        preview_text += f"文件数量: {len(self.merge_files)}\n"
        preview_text += f"输出文件名: {self.merge_output_name_var.get()}\n"
        preview_text += f"输出格式: {self.merge_output_format_var.get()}\n"
        preview_text += f"输出目录: {self.merge_output_dir_var.get()}\n\n"
        
        preview_text += "=== 文件列表 ===\n"
        total_count = 0
        for i, file_path in enumerate(self.merge_files):
            file_info = self.merger.get_file_info(file_path)
            if 'error' not in file_info:
                preview_text += f"{i+1}. {os.path.basename(file_path)} ({file_info.get('format', '--')}) - {file_info.get('count', '--')} 行\n"
                total_count += file_info.get('count', 0)
            else:
                preview_text += f"{i+1}. {os.path.basename(file_path)} - 错误: {file_info['error']}\n"
        
        preview_text += f"\n=== 合并结果 ===\n"
        preview_text += f"预计总行数: {total_count}\n"
        preview_text += f"预计输出文件: {self.merge_output_name_var.get()}.{self.merge_output_format_var.get().lower() if self.merge_output_format_var.get() != '自动检测' else 'srt'}\n"
        
        self.merge_preview_text.insert(tk.END, preview_text)
    
    def start_merge(self):
        """开始合并"""
        if not hasattr(self, 'merge_files') or not self.merge_files:
            messagebox.showwarning("警告", "请先选择要合并的文件")
            return
        
        # 确定输出格式
        output_format = self.merge_output_format_var.get()
        if output_format == "自动检测":
            # 根据第一个文件确定格式
            first_file = self.merge_files[0]
            if first_file.lower().endswith('.srt'):
                output_format = 'srt'
            elif first_file.lower().endswith('.ass'):
                output_format = 'ass'
            else:
                output_format = 'srt'  # 默认
        else:
            output_format = output_format.lower()
        
        # 构建输出路径
        output_name = self.merge_output_name_var.get()
        if not output_name:
            output_name = "merged_subtitles"
        
        output_path = os.path.join(self.merge_output_dir_var.get(), f"{output_name}.{output_format}")
        
        # 显示进度
        self.merge_progress.grid()
        self.merge_progress['value'] = 0
        self.merge_status_label.config(text="正在合并...")
        self.merge_status_indicator.config(text="🔄")
        
        try:
            # 执行合并
            result = self.merger.merge_files(self.merge_files, output_path)
            
            if result['success']:
                self.merge_progress['value'] = 100
                self.merge_status_label.config(text="合并完成")
                self.merge_status_indicator.config(text="🟢")
                
                messagebox.showinfo("成功", f"合并完成！\n\n输出文件: {result['output_file']}\n合并行数: {result['merged_count']}")
                
                # 更新预览
                self.merge_preview_text.delete(1.0, tk.END)
                self.merge_preview_text.insert(tk.END, f"合并完成！\n\n输出文件: {result['output_file']}\n合并行数: {result['merged_count']}\n总时长: {result.get('total_duration', '--')}")
            else:
                self.merge_status_label.config(text="合并失败")
                self.merge_status_indicator.config(text="🔴")
                messagebox.showerror("错误", f"合并失败: {result['error']}")
        
        except Exception as e:
            self.merge_status_label.config(text="合并失败")
            self.merge_status_indicator.config(text="🔴")
            messagebox.showerror("错误", f"合并过程中发生错误: {str(e)}")
        
        finally:
            self.merge_progress.grid_remove()

if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()