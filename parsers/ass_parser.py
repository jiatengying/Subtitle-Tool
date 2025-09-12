#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASS字幕文件解析器
"""

import re
from typing import List, Dict, Tuple


class ASSParser:
    """ASS字幕解析器"""
    
    def __init__(self):
        self.subtitles = []
        self.script_info = ""
        self.styles = ""
        self.file_info = {}
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        解析ASS文件
        
        Args:
            file_path: ASS文件路径
            
        Returns:
            字幕列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            subtitles, file_info, script_info, styles = self.parse(content)
            
            # 为合并器添加必要的字段
            for subtitle in subtitles:
                subtitle['number'] = len(subtitles)  # 临时编号，合并时会重新分配
                # 转换时间格式为datetime对象
                subtitle['start_time'] = self._seconds_to_datetime(subtitle['start_seconds'])
                subtitle['end_time'] = self._seconds_to_datetime(subtitle['end_seconds'])
            
            return subtitles
            
        except Exception as e:
            print(f"解析ASS文件失败: {e}")
            return []
    
    def _seconds_to_datetime(self, seconds: float):
        """将秒数转换为datetime对象"""
        from datetime import datetime, timedelta
        return datetime(1900, 1, 1) + timedelta(seconds=seconds)
    
    def parse(self, content: str) -> Tuple[List[Dict], Dict, str, str]:
        """
        解析ASS文件内容
        
        Args:
            content: ASS文件内容
            
        Returns:
            (字幕列表, 文件信息, 脚本信息, 样式信息)
        """
        self.subtitles = []
        lines = content.split('\n')
        in_events = False
        
        # 解析文件结构
        script_info_lines = []
        styles_lines = []
        
        for line in lines:
            line = line.strip()
            if line == '[Script Info]':
                in_events = False
                continue
            elif line == '[V4+ Styles]':
                in_events = False
                continue
            elif line == '[Events]':
                in_events = True
                continue
            elif line.startswith('[') and line not in ['[Script Info]', '[V4+ Styles]', '[Events]']:
                in_events = False
                continue
                
            if in_events and line.startswith('Dialogue:'):
                # 解析Dialogue行
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    start_time = parts[1]
                    end_time = parts[2]
                    text = parts[9]
                    
                    self.subtitles.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text,
                        'start_seconds': self.time_to_seconds(start_time),
                        'end_seconds': self.time_to_seconds(end_time)
                    })
            elif not in_events:
                if '[Script Info]' in content[:content.find(line)]:
                    script_info_lines.append(line)
                elif '[V4+ Styles]' in content[:content.find(line)]:
                    styles_lines.append(line)
        
        self.script_info = '\n'.join(script_info_lines)
        self.styles = '\n'.join(styles_lines)
        
        # 计算文件信息
        self.file_info = self._calculate_file_info()
        
        return self.subtitles, self.file_info, self.script_info, self.styles
    
    def time_to_seconds(self, time_str: str) -> float:
        """将ASS时间字符串转换为秒数"""
        try:
            # 格式: H:MM:SS.cc
            time_part, centisec_part = time_str.split('.')
            h, m, s = map(int, time_part.split(':'))
            cs = int(centisec_part)
            return h * 3600 + m * 60 + s + cs / 100.0
        except:
            return 0.0
    
    def seconds_to_time(self, seconds: float) -> str:
        """将秒数转换为ASS时间字符串"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"
    
    def _calculate_file_info(self) -> Dict:
        """计算文件统计信息"""
        if not self.subtitles:
            return {}
        
        total_count = len(self.subtitles)
        start_time = self.subtitles[0]['start_time']
        end_time = self.subtitles[-1]['end_time']
        
        return {
            'total_count': total_count,
            'start_time': start_time,
            'end_time': end_time,
            'duration_seconds': self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
        }
    
    def split_by_time_range(self, start_time: str, end_time: str, split_count: int) -> List[List[Dict]]:
        """按时间范围分割"""
        start_seconds = self.time_to_seconds(start_time)
        end_seconds = self.time_to_seconds(end_time)
        duration = end_seconds - start_seconds
        split_duration = duration / split_count
        
        splits = []
        for i in range(split_count):
            split_start = start_seconds + i * split_duration
            split_end = start_seconds + (i + 1) * split_duration
            
            split_subtitles = [sub for sub in self.subtitles 
                             if split_start <= sub['start_seconds'] < split_end]
            splits.append(split_subtitles)
        
        return splits
    
    def split_by_dialog_count(self, dialog_count: int, split_count: int) -> List[List[Dict]]:
        """按对话数量分割"""
        splits = []
        for i in range(split_count):
            start_idx = i * dialog_count
            end_idx = min((i + 1) * dialog_count, len(self.subtitles))
            splits.append(self.subtitles[start_idx:end_idx])
        
        return splits
    
    def generate_ass_content(self, script_info: str, styles: str, dialogues: List[Dict]) -> str:
        """生成ASS文件内容"""
        content = []
        
        # 添加脚本信息
        if script_info.strip():
            content.append('[Script Info]')
            content.append(script_info)
            content.append("")
        
        # 添加样式信息
        if styles.strip():
            content.append('[V4+ Styles]')
            content.append(styles)
            content.append("")
        
        # 添加事件
        content.append('[Events]')
        content.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
        
        for dialogue in dialogues:
            dialogue_line = f"Dialogue: 0,{dialogue['start_time']},{dialogue['end_time']},Default,,0,0,0,,{dialogue['text']}"
            content.append(dialogue_line)
        
        return '\n'.join(content)
