#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试行级文本对比功能
"""

import tkinter as tk
from ui.text_compare import TextCompareWindow

def test_text_compare():
    """测试行级文本对比功能"""
    root = tk.Tk()
    root.title("行级文本对比测试")
    
    # 创建文本对比窗口
    compare_window = TextCompareWindow(root)
    compare_window.open()
    
    # 设置测试文本
    text_a = """这是第一行文本
这是第二行文本
这是第三行文本
这是第四行文本"""
    
    text_b = """这是第一行文本
这是修改的第二行文本
这是新增的第三行文本
这是第四行文本
这是新增的第五行文本"""
    
    # 设置文本内容
    compare_window.set_texts(text_a, text_b)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    test_text_compare()
