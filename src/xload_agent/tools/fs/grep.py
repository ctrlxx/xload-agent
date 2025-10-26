import re
import fnmatch
from pathlib import Path
from typing import Optional, List, Dict, Pattern

from google.adk.tools.tool_context import ToolContext

def grep_tool(
    pattern: str,
    path: str,
    recursive: bool = True,
    file_pattern: Optional[List[str]] = None,
    ignore: Optional[List[str]] = None,
    case_sensitive: bool = False,
    max_results: int = 1000,
    tool_context: ToolContext = None
) -> Dict:
    """在指定路径中搜索匹配正则表达式的文本行，类似系统的grep命令。

    Args:
        pattern: 要搜索的正则表达式模式。
        path: 要搜索的绝对路径（文件或目录）。
        recursive: 是否递归搜索子目录，默认为True。
        file_pattern: 可选的文件匹配模式数组，用于限制搜索的文件类型。
        ignore: 可选的文件/目录忽略模式数组。
        case_sensitive: 是否区分大小写，默认为False（不区分大小写）。
        max_results: 最大返回结果数量，默认为1000。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        dict: 包含搜索结果的字典，格式为{"status": "success", "matches": [...], "stats": {...}}
             或错误信息{"status": "error", "message": "错误描述"}
    """
    # 默认忽略模式
    DEFAULT_IGNORE_PATTERNS = [
        "*.pyc", "__pycache__", ".git", ".svn", ".hg", ".DS_Store",
        "*.tmp", "*.temp", "*.log", ".idea", "*.vscode", "node_modules"
    ]
    
    # 验证路径是否为绝对路径
    _path = Path(path)
    if not _path.is_absolute():
        return {
            "status": "error",
            "message": f"错误: 路径 {path} 不是绝对路径。请提供绝对路径。"
        }
    
    # 验证路径是否存在
    if not _path.exists():
        return {
            "status": "error",
            "message": f"错误: 路径 {path} 不存在。请提供有效的路径。"
        }
    
    # 编译正则表达式
    try:
        regex_flags = 0 if case_sensitive else re.IGNORECASE
        regex_pattern = re.compile(pattern, regex_flags)
    except re.error as e:
        return {
            "status": "error",
            "message": f"错误: 无效的正则表达式 '{pattern}': {str(e)}"
        }
    
    # 合并忽略模式
    ignore_patterns = (ignore or []) + DEFAULT_IGNORE_PATTERNS
    
    # 统计信息
    stats = {
        "files_searched": 0,
        "files_matched": 0,
        "lines_matched": 0,
        "results_truncated": False
    }
    
    # 匹配结果
    matches = []
    
    # 检查文件是否应该被忽略
    def should_ignore(path: Path) -> bool:
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True
        return False
    
    # 检查文件是否应该被搜索
    def should_search_file(path: Path) -> bool:
        # 首先检查是否应该被忽略
        if should_ignore(path):
            return False
        
        # 如果指定了文件模式，则检查是否匹配
        if file_pattern:
            for pattern in file_pattern:
                if fnmatch.fnmatch(path.name, pattern):
                    return True
            return False
        
        # 默认搜索所有非忽略的文件
        return True
    
    # 搜索单个文件
    def search_file(file_path: Path) -> None:
        nonlocal stats, matches
        
        stats["files_searched"] += 1
        
        # 检查是否超过最大结果限制
        if len(matches) >= max_results:
            stats["results_truncated"] = True
            return
        
        try:
            # 尝试以文本方式打开文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_matched = False
                
                for line_num, line in enumerate(f, 1):
                    # 检查是否超过最大结果限制
                    if len(matches) >= max_results:
                        stats["results_truncated"] = True
                        break
                    
                    # 搜索匹配
                    match = regex_pattern.search(line)
                    if match:
                        if not file_matched:
                            file_matched = True
                            stats["files_matched"] += 1
                        
                        stats["lines_matched"] += 1
                        
                        # 提取匹配的行内容（去除末尾换行）
                        line_content = line.rstrip('\n\r')
                        
                        # 计算上下文（前10个字符和后10个字符）
                        match_start, match_end = match.span()
                        context_start = max(0, match_start - 10)
                        context_end = min(len(line_content), match_end + 10)
                        
                        # 构建匹配结果
                        match_result = {
                            "file": str(file_path),
                            "line": line_num,
                            "content": line_content,
                            "match_start": match_start,
                            "match_end": match_end,
                            "context": {
                                "prefix": line_content[context_start:match_start],
                                "match": line_content[match_start:match_end],
                                "suffix": line_content[match_end:context_end]
                            }
                        }
                        
                        matches.append(match_result)
        
        except PermissionError:
            # 忽略没有权限访问的文件
            pass
        except Exception as e:
            # 忽略无法读取的文件（例如二进制文件）
            pass
    
    # 开始搜索
    if _path.is_file():
        # 单个文件搜索
        if should_search_file(_path):
            search_file(_path)
        else:
            return {
                "status": "error",
                "message": f"错误: 文件 {path} 被忽略模式过滤。"
            }
    else:
        # 目录搜索
        if recursive:
            # 递归搜索
            for root, dirs, files in _path.walk():
                # 过滤目录
                dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]
                
                # 搜索文件
                for file in files:
                    file_path = Path(root) / file
                    if should_search_file(file_path):
                        search_file(file_path)
                    
                    # 检查是否超过最大结果限制
                    if stats["results_truncated"]:
                        break
                
                if stats["results_truncated"]:
                    break
        else:
            # 非递归搜索
            try:
                for item in _path.iterdir():
                    if item.is_file() and should_search_file(item):
                        search_file(item)
                    
                    # 检查是否超过最大结果限制
                    if stats["results_truncated"]:
                        break
            except PermissionError:
                return {
                    "status": "error",
                    "message": f"错误: 没有权限访问路径 {path}。"
                }
    
    # 返回结果
    return {
        "status": "success",
        "pattern": pattern,
        "path": path,
        "recursive": recursive,
        "case_sensitive": case_sensitive,
        "matches": matches,
        "stats": stats
    }

def grep_tool_formatted(
    pattern: str,
    path: str,
    recursive: bool = True,
    file_pattern: Optional[List[str]] = None,
    ignore: Optional[List[str]] = None,
    case_sensitive: bool = False,
    max_results: int = 1000,
    tool_context: ToolContext = None
) -> str:
    """在指定路径中搜索匹配正则表达式的文本行，并返回格式化的结果。

    Args:
        pattern: 要搜索的正则表达式模式。
        path: 要搜索的绝对路径（文件或目录）。
        recursive: 是否递归搜索子目录，默认为True。
        file_pattern: 可选的文件匹配模式数组，用于限制搜索的文件类型。
        ignore: 可选的文件/目录忽略模式数组。
        case_sensitive: 是否区分大小写，默认为False（不区分大小写）。
        max_results: 最大返回结果数量，默认为1000。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        str: 格式化的搜索结果或错误消息。
    """
    result = grep_tool(
        pattern, path, recursive, file_pattern, ignore,
        case_sensitive, max_results, tool_context
    )
    
    if result["status"] == "error":
        return result["message"]
    
    # 生成格式化的输出
    formatted_lines = [
        f"搜索结果: '{result['pattern']}' 在 '{result['path']}'",
        f"搜索选项: 递归={result['recursive']}, 区分大小写={result['case_sensitive']}"
    ]
    
    if file_pattern:
        formatted_lines.append(f"文件过滤: {', '.join(file_pattern)}")
    
    stats = result["stats"]
    formatted_lines.append(
        f"\n统计信息: 搜索 {stats['files_searched']} 个文件, "
        f"找到 {stats['files_matched']} 个匹配文件, "
        f"共 {stats['lines_matched']} 个匹配行"
    )
    
    if stats["results_truncated"]:
        formatted_lines.append(f"注意: 结果已截断，显示前{max_results}个匹配项")
    
    if not result["matches"]:
        formatted_lines.append("\n未找到匹配项。")
    else:
        formatted_lines.append("\n匹配详情:")
        formatted_lines.append("=" * 80)
        
        # 按文件分组显示结果
        current_file = None
        for match in result["matches"]:
            if match["file"] != current_file:
                current_file = match["file"]
                formatted_lines.append(f"\n文件: {current_file}")
                formatted_lines.append("-" * 80)
            
            # 格式化行号和内容
            line_info = f"{match['line']:5d}: "
            
            # 高亮显示匹配部分
            content = match['content']
            match_start = match['match_start']
            match_end = match['match_end']
            
            # 构建带高亮的行
            # 在终端中可以使用ANSI颜色，但这里我们使用特殊标记
            highlighted_line = (
                line_info + 
                content[:match_start] + 
                "[MATCH]" + content[match_start:match_end] + "[/MATCH]" + 
                content[match_end:]
            )
            
            formatted_lines.append(highlighted_line)
    
    formatted_lines.append("\n" + "=" * 80)
    
    return "\n".join(formatted_lines)

if __name__ == "__main__":
    # 示例用法
    import os
    
    # 获取当前目录作为测试路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 测试1: 搜索关键字
    print("测试1: 搜索关键字 'tool'")
    print(grep_tool_formatted(pattern="tool", path=current_dir, recursive=True))
    print("\n" + "="*80 + "\n")
    
    # 测试2: 搜索特定文件类型
    print("测试2: 在Python文件中搜索 'def'")
    print(grep_tool_formatted(pattern="def", path=current_dir, file_pattern=["*.py"]))
    print("\n" + "="*80 + "\n")
    
    # 测试3: 区分大小写搜索
    print("测试3: 区分大小写搜索 'Tool'")
    print(grep_tool_formatted(pattern="Tool", path=current_dir, case_sensitive=True))
    print("\n" + "="*80 + "\n")
    
    # 测试4: 正则表达式搜索
    print("测试4: 正则表达式搜索函数定义 'def \w+\(' ")
    print(grep_tool_formatted(pattern="def \w+\(", path=current_dir, file_pattern=["*.py"]))
    print("\n" + "="*80 + "\n")
    
    # 测试5: 错误处理 - 相对路径
    print("测试5: 错误处理 - 相对路径")
    print(grep_tool_formatted(pattern="test", path="./relative/path"))
    print("\n" + "="*80 + "\n")
    
    # 测试6: 错误处理 - 无效的正则表达式
    print("测试6: 错误处理 - 无效的正则表达式")
    print(grep_tool_formatted(pattern="[a-z", path=current_dir))