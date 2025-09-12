#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕分割工具主程序入口
"""

import tkinter as tk
from ui.main_window import MainWindow


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass  # 如果没有图标文件就忽略
    
    # 创建应用实例
    app = MainWindow(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
