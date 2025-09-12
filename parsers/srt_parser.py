#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT字幕文件解析器
"""

import re
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class SRTParser:
    """SRT字幕解析器"""
    
    def __init__(self):
        self.subtitles = []
        self.file_info = {}
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        解析SRT文件
        
        Args:
            file_path: SRT文件路径
            
        Returns:
            字幕列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            subtitles, file_info = self.parse(content)
            
            # 为合并器添加必要的字段
            for subtitle in subtitles:
                subtitle['number'] = subtitle['index']  # 使用原有的index作为number
                # 转换时间格式为datetime对象
                subtitle['start_time'] = self._seconds_to_datetime(subtitle['start_seconds'])
                subtitle['end_time'] = self._seconds_to_datetime(subtitle['end_seconds'])
            
            return subtitles
            
        except Exception as e:
            print(f"解析SRT文件失败: {e}")
            return []
    
    def _seconds_to_datetime(self, seconds: float):
        """将秒数转换为datetime对象"""
        return datetime(1900, 1, 1) + timedelta(seconds=seconds)
    
    def parse(self, content: str) -> Tuple[List[Dict], Dict]:
        """
        解析SRT文件内容
        
        Args:
            content: SRT文件内容
            
        Returns:
            (字幕列表, 文件信息)
        """
        self.subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    # 解析序号
                    index = int(lines[0])
                    
                    # 解析时间轴
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                        
                        # 解析文本内容
                        text = '\n'.join(lines[2:])
                        
                        self.subtitles.append({
                            'index': index,
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text,
                            'start_seconds': self.time_to_seconds(start_time),
                            'end_seconds': self.time_to_seconds(end_time)
                        })
                except ValueError:
                    continue
        
        # 计算文件信息
        self.file_info = self._calculate_file_info()
        
        return self.subtitles, self.file_info
    
    def time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        try:
            # 格式: HH:MM:SS,mmm
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            return h * 3600 + m * 60 + s + ms / 1000.0
        except:
            return 0.0
    
    def seconds_to_time(self, seconds: float) -> str:
        """将秒数转换为时间字符串"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"
    
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
    
    def split_by_index_range(self, start_index: int, end_index: int, split_count: int) -> List[List[Dict]]:
        """按序号范围分割"""
        total_range = end_index - start_index + 1
        items_per_split = total_range // split_count
        
        splits = []
        for i in range(split_count):
            split_start = start_index + i * items_per_split
            split_end = min(split_start + items_per_split - 1, end_index)
            
            split_subtitles = [sub for sub in self.subtitles 
                             if split_start <= sub['index'] <= split_end]
            splits.append(split_subtitles)
        
        return splits
    
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
    
    def generate_srt_content(self, subtitles: List[Dict]) -> str:
        """生成SRT文件内容"""
        content = []
        for i, sub in enumerate(subtitles, 1):
            content.append(str(i))
            content.append(f"{sub['start_time']} --> {sub['end_time']}")
            content.append(sub['text'])
            content.append("")
        return '\n'.join(content)
