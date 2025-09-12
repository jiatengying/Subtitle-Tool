"""
字幕合并器模块
用于合并分割的字幕文件
"""

import os
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from parsers.srt_parser import SRTParser
from parsers.ass_parser import ASSParser


class SubtitleMerger:
    """字幕合并器"""
    
    def __init__(self):
        self.srt_parser = SRTParser()
        self.ass_parser = ASSParser()
    
    def merge_files(self, file_paths: List[str], output_path: str) -> Dict:
        """
        合并字幕文件
        
        Args:
            file_paths: 要合并的文件路径列表（按顺序）
            output_path: 输出文件路径
            
        Returns:
            合并结果字典
        """
        try:
            # 检查文件是否存在
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return {
                        'success': False,
                        'error': f'文件不存在: {file_path}',
                        'merged_count': 0
                    }
            
            # 检测文件格式
            file_format = self._detect_format(file_paths[0])
            if not file_format:
                return {
                    'success': False,
                    'error': '不支持的文件格式',
                    'merged_count': 0
                }
            
            if file_format == 'SRT':
                return self._merge_srt_files(file_paths, output_path)
            else:  # ASS
                return self._merge_ass_files(file_paths, output_path)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'合并失败: {str(e)}',
                'merged_count': 0
            }
    
    def _merge_ass_files(self, file_paths: List[str], output_path: str) -> Dict:
        """合并ASS文件"""
        try:
            # 读取第一个文件获取头部信息
            first_file = file_paths[0]
            with open(first_file, 'r', encoding='utf-8') as f:
                first_content = f.read()
            
            # 提取头部信息
            script_info_match = re.search(r'\[Script Info\].*?(?=\[V4\+ Styles\]|\[Events\]|$)', first_content, re.DOTALL)
            styles_match = re.search(r'\[V4\+ Styles\].*?(?=\[Events\]|$)', first_content, re.DOTALL)
            
            # 收集所有Dialogue行
            all_dialogues = []
            
            for file_path in file_paths:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('Dialogue:'):
                            all_dialogues.append(line)
            
            # 写入合并后的文件
            with open(output_path, 'w', encoding='utf-8') as f:
                # 写入[Script Info]
                if script_info_match:
                    f.write(script_info_match.group(0) + '\n\n')
                else:
                    f.write('[Script Info]\n')
                    f.write('Title: Merged Subtitles\n')
                    f.write('ScriptType: v4.00+\n\n')
                
                # 写入[V4+ Styles]
                if styles_match:
                    f.write(styles_match.group(0) + '\n\n')
                else:
                    f.write('[V4+ Styles]\n')
                    f.write('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n')
                    f.write('Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n')
                
                # 写入[Events]
                f.write('[Events]\n')
                f.write('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
                
                # 写入所有Dialogue行
                for dialogue in all_dialogues:
                    f.write(dialogue + '\n')
            
            return {
                'success': True,
                'merged_count': len(all_dialogues),
                'output_file': output_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'合并ASS文件失败: {str(e)}',
                'merged_count': 0
            }
    
    def _merge_srt_files(self, file_paths: List[str], output_path: str) -> Dict:
        """合并SRT文件"""
        try:
            all_subtitles = []
            subtitle_number = 1
            
            for file_path in file_paths:
                subtitles = self.srt_parser.parse_file(file_path)
                for subtitle in subtitles:
                    subtitle['number'] = subtitle_number
                    all_subtitles.append(subtitle)
                    subtitle_number += 1
            
            # 写入SRT文件
            self._write_srt_file(all_subtitles, output_path)
            
            return {
                'success': True,
                'merged_count': len(all_subtitles),
                'output_file': output_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'合并SRT文件失败: {str(e)}',
                'merged_count': 0
            }
    
    def _detect_format(self, file_path: str) -> Optional[str]:
        """检测文件格式"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.srt':
            return 'SRT'
        elif ext == '.ass':
            return 'ASS'
        return None
    
    def _is_dialogue_only_file(self, file_path: str) -> bool:
        """检查文件是否只包含Dialogue行"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                return first_line.startswith('Dialogue:')
        except:
            return False
    
    def _parse_dialogue_only_file(self, file_path: str) -> List[Dict]:
        """解析只包含Dialogue行的ASS文件"""
        subtitles = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line.startswith('Dialogue:'):
                        # 解析Dialogue行
                        parts = line.split(',', 9)
                        if len(parts) >= 10:
                            start_time = parts[1]
                            end_time = parts[2]
                            text = parts[9]
                            
                            # 转换时间格式
                            start_datetime = self._ass_time_to_datetime(start_time)
                            end_datetime = self._ass_time_to_datetime(end_time)
                            
                            subtitles.append({
                                'number': line_num,
                                'start_time': start_datetime,
                                'end_time': end_datetime,
                                'text': text
                            })
        except Exception as e:
            print(f"解析Dialogue文件失败 {file_path}: {e}")
            return []
        
        return subtitles
    
    def _ass_time_to_datetime(self, time_str: str):
        """将ASS时间字符串转换为datetime对象"""
        try:
            # 格式: H:MM:SS.CC
            time_part, centisec_part = time_str.split('.')
            h, m, s = map(int, time_part.split(':'))
            cs = int(centisec_part)
            
            # 转换为秒数
            total_seconds = h * 3600 + m * 60 + s + cs / 100.0
            
            # 转换为datetime对象
            return datetime(1900, 1, 1) + timedelta(seconds=total_seconds)
        except:
            return datetime(1900, 1, 1)
    
    def _adjust_timeline(self, subtitles: List[Dict], offset: timedelta) -> List[Dict]:
        """调整字幕时间轴"""
        adjusted_subtitles = []
        
        for subtitle in subtitles:
            adjusted_subtitle = subtitle.copy()
            adjusted_subtitle['start_time'] = subtitle['start_time'] + offset
            adjusted_subtitle['end_time'] = subtitle['end_time'] + offset
            adjusted_subtitles.append(adjusted_subtitle)
        
        return adjusted_subtitles
    
    def _update_subtitle_numbers(self, subtitles: List[Dict], start_number: int) -> List[Dict]:
        """更新字幕序号"""
        updated_subtitles = []
        
        for i, subtitle in enumerate(subtitles):
            updated_subtitle = subtitle.copy()
            updated_subtitle['number'] = start_number + i + 1
            updated_subtitles.append(updated_subtitle)
        
        return updated_subtitles
    
    def _write_srt_file(self, subtitles: List[Dict], output_path: str):
        """写入SRT文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for subtitle in subtitles:
                f.write(f"{subtitle['number']}\n")
                f.write(f"{self._format_srt_time(subtitle['start_time'])} --> {self._format_srt_time(subtitle['end_time'])}\n")
                f.write(f"{subtitle['text']}\n\n")
    
    def _write_ass_file(self, subtitles: List[Dict], output_path: str, template_file: str):
        """写入ASS文件"""
        # 读取模板文件的头部信息
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取[Script Info]和[V4+ Styles]部分
        script_info_match = re.search(r'\[Script Info\].*?(?=\[V4\+ Styles\]|\[Events\]|$)', content, re.DOTALL)
        styles_match = re.search(r'\[V4\+ Styles\].*?(?=\[Events\]|$)', content, re.DOTALL)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入[Script Info]
            if script_info_match:
                f.write(script_info_match.group(0) + '\n\n')
            else:
                f.write('[Script Info]\n')
                f.write('Title: Merged Subtitles\n')
                f.write('ScriptType: v4.00+\n\n')
            
            # 写入[V4+ Styles]
            if styles_match:
                f.write(styles_match.group(0) + '\n\n')
            else:
                f.write('[V4+ Styles]\n')
                f.write('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n')
                f.write('Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n')
            
            # 写入[Events]
            f.write('[Events]\n')
            f.write('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
            
            for subtitle in subtitles:
                start_time = self._format_ass_time(subtitle['start_time'])
                end_time = self._format_ass_time(subtitle['end_time'])
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{subtitle['text']}\n")
    
    def _format_srt_time(self, time_obj: datetime) -> str:
        """格式化SRT时间"""
        return time_obj.strftime('%H:%M:%S,%f')[:-3]  # 去掉最后3位微秒
    
    def _format_ass_time(self, time_obj: datetime) -> str:
        """格式化ASS时间"""
        # ASS时间格式: H:MM:SS.CC
        hours = time_obj.hour
        minutes = time_obj.minute
        seconds = time_obj.second
        centiseconds = int(time_obj.microsecond / 10000)  # 微秒转换为厘秒
        
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    
    def get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return {'error': '文件不存在'}
            
            file_format = self._detect_format(file_path)
            if not file_format:
                return {'error': '不支持的文件格式'}
            
            # 解析文件
            if file_format == 'SRT':
                subtitles = self.srt_parser.parse_file(file_path)
            else:  # ASS
                subtitles = self.ass_parser.parse_file(file_path)
            
            if not subtitles:
                return {'error': '无法解析文件内容'}
            
            # 计算信息
            file_size = os.path.getsize(file_path)
            start_time = subtitles[0]['start_time']
            end_time = subtitles[-1]['end_time']
            duration = end_time - start_time
            
            # 获取文件的实际行数
            total_lines = 0
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines = len(f.readlines())
            except:
                total_lines = 0
            
            return {
                'format': file_format,
                'count': total_lines,  # 显示文件行数而不是字幕条数
                'start_time': start_time.strftime('%H:%M:%S'),
                'end_time': end_time.strftime('%H:%M:%S'),
                'duration': str(duration),
                'file_size': file_size
            }
            
        except Exception as e:
            return {'error': f'解析失败: {str(e)}'}
