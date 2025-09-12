#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕分割器核心模块
"""

import os
from typing import List, Dict, Callable
from parsers.srt_parser import SRTParser
from parsers.ass_parser import ASSParser


class SubtitleSplitter:
    """字幕分割器"""
    
    def __init__(self):
        self.srt_parser = SRTParser()
        self.ass_parser = ASSParser()
        self.current_file = None
        self.file_format = None
        self.subtitle_data = []
        self.file_info = {}
        self.script_info = ""
        self.styles = ""
    
    def load_file(self, file_path: str) -> bool:
        """
        加载字幕文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file = file_path
            
            # 检测文件格式并解析
            if file_path.lower().endswith('.srt'):
                self.file_format = 'SRT'
                self.subtitle_data, self.file_info = self.srt_parser.parse(content)
                self.script_info = ""
                self.styles = ""
            elif file_path.lower().endswith('.ass'):
                self.file_format = 'ASS'
                self.subtitle_data, self.file_info, self.script_info, self.styles = self.ass_parser.parse(content)
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"加载文件失败: {str(e)}")
            return False
    
    def get_file_info(self) -> Dict:
        """获取文件信息"""
        if not self.file_info:
            return {}
        
        file_size = os.path.getsize(self.current_file) if self.current_file else 0
        
        # 获取文件的实际行数
        total_lines = 0
        if self.current_file:
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    total_lines = len(f.readlines())
            except:
                total_lines = 0
        
        return {
            'filename': os.path.basename(self.current_file) if self.current_file else "",
            'format': self.file_format,
            'total_count': total_lines,  # 显示文件行数而不是字幕条数
            'start_time': self.file_info.get('start_time', '00:00:00'),
            'end_time': self.file_info.get('end_time', '00:00:00'),
            'file_size': file_size,
            'duration_seconds': self.file_info.get('duration_seconds', 0)
        }
    
    def split_srt_by_index(self, start_index: int, end_index: int, split_count: int) -> List[str]:
        """SRT按序号分割"""
        splits = self.srt_parser.split_by_index_range(start_index, end_index, split_count)
        return self._save_splits(splits, 'srt')
    
    def split_by_lines(self, lines_per_split: int, split_count: int, batch_mode: str = "uniform") -> List[str]:
        """按文件行数分割（通用方法，适用于ASS和SRT）"""
        if not self.current_file:
            return []
        
        try:
            # 读取原始文件的所有行
            with open(self.current_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            total_lines = len(all_lines)
            saved_files = []
            
            if batch_mode == "smart":
                # 智能模式：根据文件行数自动计算每份行数
                lines_per_split = total_lines // split_count
                if lines_per_split == 0:
                    lines_per_split = 1  # 至少1行
                actual_split_count = split_count
            else:
                # 统一模式：使用用户指定的行数
                actual_split_count = min(split_count, (total_lines + lines_per_split - 1) // lines_per_split)
            
            for i in range(actual_split_count):
                start_line = i * lines_per_split
                if batch_mode == "smart" and i == actual_split_count - 1:
                    # 智能模式下，最后一个文件包含所有剩余行
                    end_line = total_lines
                else:
                    end_line = min((i + 1) * lines_per_split, total_lines)
                
                # 获取分割的行内容
                split_lines = all_lines[start_line:end_line]
                
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                extension = os.path.splitext(self.current_file)[1]
                output_file = f"{base_name}_分割{i+1}{extension}"
                
                # 写入分割文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.writelines(split_lines)
                
                saved_files.append(output_file)
                print(f"已创建分割文件: {output_file} (行数: {start_line+1}-{end_line})")
            
            return saved_files
            
        except Exception as e:
            print(f"按行数分割失败: {str(e)}")
            return []
    
    def split_srt_by_count(self, dialog_count: int, split_count: int) -> List[str]:
        """SRT按文本行数分割（已废弃，使用split_by_lines替代）"""
        return self.split_by_lines(dialog_count, split_count)
    
    def split_ass_by_time(self, start_time: str, end_time: str, split_count: int) -> List[str]:
        """ASS按时间分割"""
        splits = self.ass_parser.split_by_time_range(start_time, end_time, split_count)
        return self._save_splits(splits, 'ass')
    
    def split_ass_by_count(self, dialog_count: int, split_count: int) -> List[str]:
        """ASS按对话数量分割（已废弃，使用split_by_lines替代）"""
        return self.split_by_lines(dialog_count, split_count)
    
    def _save_splits(self, splits: List[List[Dict]], format_type: str) -> List[str]:
        """保存分割结果"""
        if not self.current_file:
            return []
        
        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        saved_files = []
        
        for i, split_subtitles in enumerate(splits):
            if not split_subtitles:
                continue
                
            if format_type == 'srt':
                # 第一个分割文件保留完整SRT格式，后续文件只保留字幕行
                if i == 0:
                    content = self.srt_parser.generate_srt_content(split_subtitles)
                else:
                    content = self._generate_srt_subtitle_only(split_subtitles)
                extension = '.srt'
            else:  # ass
                # 第一个分割文件保留完整头部信息，后续文件只保留Dialogue行
                if i == 0:
                    content = self.ass_parser.generate_ass_content(
                        self.script_info, self.styles, split_subtitles
                    )
                else:
                    content = self._generate_ass_dialogue_only(split_subtitles)
                extension = '.ass'
            
            output_file = f"{base_name}_分割{i+1}{extension}"
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files.append(output_file)
            except Exception as e:
                print(f"保存文件失败 {output_file}: {str(e)}")
        
        return saved_files
    
    def _generate_srt_subtitle_only(self, subtitles: List[Dict]) -> str:
        """生成只包含字幕行的SRT内容"""
        content = []
        
        for subtitle in subtitles:
            # 生成字幕行（不包含序号）
            content.append(f"{subtitle['start_time']} --> {subtitle['end_time']}")
            content.append(subtitle['text'])
            content.append("")  # 空行分隔
        
        return '\n'.join(content)
    
    def _generate_ass_dialogue_only(self, subtitles: List[Dict]) -> str:
        """生成只包含Dialogue行的ASS内容"""
        content = []
        
        for subtitle in subtitles:
            # 转换时间格式为ASS格式
            start_time = self._format_ass_time(subtitle['start_time'])
            end_time = self._format_ass_time(subtitle['end_time'])
            
            # 生成Dialogue行
            dialogue_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{subtitle['text']}"
            content.append(dialogue_line)
        
        return '\n'.join(content)
    
    def _format_ass_time(self, time_str: str) -> str:
        """将ASS时间字符串转换为标准格式"""
        # 如果已经是标准格式，直接返回
        if ':' in time_str and '.' in time_str:
            return time_str
        
        # 如果是秒数格式，需要转换
        try:
            seconds = float(time_str)
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            centisecs = int((seconds % 1) * 100)
            return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
        except:
            return time_str
    
    def preview_split(self, method: str, **kwargs) -> List[Dict]:
        """预览分割结果"""
        if method == "srt_index":
            return self._preview_srt_index(kwargs['start_index'], kwargs['end_index'], kwargs['split_count'])
        elif method == "srt_time":
            return self._preview_srt_time(kwargs['start_time'], kwargs['end_time'], kwargs['split_count'])
        elif method == "ass_time":
            return self._preview_ass_time(kwargs['start_time'], kwargs['end_time'], kwargs['split_count'])
        elif method == "ass_count":
            return self._preview_ass_count(kwargs['dialog_count'], kwargs['split_count'])
        elif method == "line_split":
            return self._preview_line_split(kwargs['lines_per_split'], kwargs['split_count'])
        return []
    
    def _preview_srt_index(self, start_index: int, end_index: int, split_count: int) -> List[Dict]:
        """预览SRT按序号分割"""
        splits = self.srt_parser.split_by_index_range(start_index, end_index, split_count)
        return self._format_preview(splits, 'index')
    
    def _preview_srt_time(self, start_time: str, end_time: str, split_count: int) -> List[Dict]:
        """预览SRT按时间分割"""
        splits = self.srt_parser.split_by_time_range(start_time, end_time, split_count)
        return self._format_preview(splits, 'time')
    
    def _preview_ass_time(self, start_time: str, end_time: str, split_count: int) -> List[Dict]:
        """预览ASS按时间分割"""
        splits = self.ass_parser.split_by_time_range(start_time, end_time, split_count)
        return self._format_preview(splits, 'time')
    
    def _preview_ass_count(self, dialog_count: int, split_count: int) -> List[Dict]:
        """预览ASS按对话数量分割"""
        splits = self.ass_parser.split_by_dialog_count(dialog_count, split_count)
        return self._format_preview(splits, 'count')
    
    def _preview_line_split(self, lines_per_split: int, split_count: int) -> List[Dict]:
        """预览按行数分割"""
        if not self.current_file:
            return []
        
        try:
            # 读取原始文件的所有行
            with open(self.current_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            total_lines = len(all_lines)
            preview = []
            
            # 计算实际分割数量
            actual_split_count = min(split_count, (total_lines + lines_per_split - 1) // lines_per_split)
            
            for i in range(actual_split_count):
                start_line = i * lines_per_split
                end_line = min((i + 1) * lines_per_split, total_lines)
                
                preview.append({
                    'split_num': i + 1,
                    'range': f"行数{start_line+1}-{end_line}",
                    'time_range': f"共{end_line-start_line}行",
                    'count': end_line - start_line
                })
            
            return preview
            
        except Exception as e:
            print(f"预览按行数分割失败: {str(e)}")
            return []
    
    def _format_preview(self, splits: List[List[Dict]], split_type: str) -> List[Dict]:
        """格式化预览结果"""
        preview = []
        
        for i, split_subtitles in enumerate(splits):
            if not split_subtitles:
                continue
                
            if split_type == 'index':
                start_idx = split_subtitles[0]['index']
                end_idx = split_subtitles[-1]['index']
                start_time = split_subtitles[0]['start_time']
                end_time = split_subtitles[-1]['end_time']
                preview.append({
                    'split_num': i + 1,
                    'range': f"序号{start_idx}-{end_idx}",
                    'time_range': f"{start_time}-{end_time}",
                    'count': len(split_subtitles)
                })
            elif split_type == 'time':
                start_time = split_subtitles[0]['start_time']
                end_time = split_subtitles[-1]['end_time']
                preview.append({
                    'split_num': i + 1,
                    'range': f"时间范围",
                    'time_range': f"{start_time}-{end_time}",
                    'count': len(split_subtitles)
                })
            elif split_type == 'count':
                start_idx = i * len(split_subtitles) + 1
                end_idx = start_idx + len(split_subtitles) - 1
                start_time = split_subtitles[0]['start_time']
                end_time = split_subtitles[-1]['end_time']
                preview.append({
                    'split_num': i + 1,
                    'range': f"对话{start_idx}-{end_idx}",
                    'time_range': f"{start_time}-{end_time}",
                    'count': len(split_subtitles)
                })
        
        return preview
