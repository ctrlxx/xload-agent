import fnmatch
from pathlib import Path
from typing import Optional, List, Dict

from google.adk.tools.tool_context import ToolContext

def tree_tool(
    path: str,
    max_depth: int = 3,
    match: Optional[List[str]] = None,
    ignore: Optional[List[str]] = None,
    tool_context: ToolContext = None
) -> Dict:
    """列出指定目录下的所有子孙目录和文件，支持指定最大深度（默认3层）。

    Args:
        path: 要列出文件和目录的绝对路径。不允许使用相对路径。
        max_depth: 最大遍历深度，默认为3层，最大不超过3层。
        match: 可选的glob模式数组，用于匹配文件和目录。
        ignore: 可选的glob模式数组，用于忽略文件和目录。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        dict: 包含列出结果的字典，格式为{"status": "success", "tree": [...]} 
             或错误信息{"status": "error", "message": "错误描述"}
    """
    # 默认忽略模式
    DEFAULT_IGNORE_PATTERNS = [
        "*.pyc", "__pycache__", "*.swp", ".DS_Store", ".git", ".svn", ".hg",
        "*.tmp", "*.temp", "*.log", ".idea", "*.vscode", "node_modules"
    ]
    
    # 验证并限制最大深度
    max_depth = min(max(1, max_depth), 3)  # 确保深度在1到3之间
    
    # 检查路径是否为绝对路径
    _path = Path(path)
    if not _path.is_absolute():
        return {
            "status": "error",
            "message": f"错误: 路径 {path} 不是绝对路径。请提供绝对路径。"
        }
    
    # 检查路径是否存在
    if not _path.exists():
        return {
            "status": "error",
            "message": f"错误: 路径 {path} 不存在。请提供有效的路径。"
        }
    
    # 检查路径是否为目录
    if not _path.is_dir():
        return {
            "status": "error",
            "message": f"错误: 路径 {path} 不是目录。请提供有效的目录路径。"
        }
    
    # 合并忽略模式
    ignore_patterns = (ignore or []) + DEFAULT_IGNORE_PATTERNS
    
    # 递归遍历函数
    def _walk_directory(current_path: Path, current_depth: int) -> List[Dict]:
        items = []
        
        try:
            # 获取当前目录下的所有项目
            directory_items = list(current_path.iterdir())
            
            # 排序项目: 目录在前，文件在后，都按字母顺序排列
            directory_items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in directory_items:
                # 检查是否需要忽略
                should_ignore = False
                for pattern in ignore_patterns:
                    if fnmatch.fnmatch(item.name, pattern):
                        should_ignore = True
                        break
                
                if should_ignore:
                    continue
                
                # 检查是否匹配模式（如果提供）
                if match:
                    matched = False
                    for pattern in match:
                        if fnmatch.fnmatch(item.name, pattern):
                            matched = True
                            break
                    if not matched:
                        continue
                
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item)
                }
                
                # 如果是目录且未达到最大深度，递归遍历
                if item.is_dir() and current_depth < max_depth:
                    item_info["children"] = _walk_directory(item, current_depth + 1)
                
                items.append(item_info)
        
        except PermissionError:
            # 没有权限访问的目录添加为特殊项目
            items.append({
                "name": current_path.name,
                "type": "directory",
                "path": str(current_path),
                "error": "Permission denied"
            })
        except Exception as e:
            # 其他异常处理
            items.append({
                "name": current_path.name,
                "type": "directory",
                "path": str(current_path),
                "error": str(e)
            })
        
        return items
    
    # 开始递归遍历
    tree_structure = _walk_directory(_path, 1)
    
    # 计算统计信息
    dir_count = 0
    file_count = 0
    
    def _count_items(items):
        nonlocal dir_count, file_count
        for item in items:
            if item["type"] == "directory":
                dir_count += 1
                if "children" in item:
                    _count_items(item["children"])
            else:
                file_count += 1
    
    _count_items(tree_structure)
    
    return {
        "status": "success",
        "path": path,
        "max_depth": max_depth,
        "tree": tree_structure,
        "directories": dir_count,
        "files": file_count,
        "total": dir_count + file_count
    }

def tree_tool_formatted(
    path: str,
    max_depth: int = 3,
    match: Optional[List[str]] = None,
    ignore: Optional[List[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """列出指定目录下的所有子孙目录和文件，并返回格式化的树形字符串结果。

    Args:
        path: 要列出文件和目录的绝对路径。不允许使用相对路径。
        max_depth: 最大遍历深度，默认为3层，最大不超过3层。
        match: 可选的glob模式数组，用于匹配文件和目录。
        ignore: 可选的glob模式数组，用于忽略文件和目录。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        str: 格式化的树形结果或错误消息。
    """
    result = tree_tool(path, max_depth, match, ignore, tool_context)
    
    if result["status"] == "error":
        return result["message"]
    
    # 生成格式化的树形输出
    def _format_tree(items, level=0, prefix="") -> str:
        output = []
        
        for i, item in enumerate(items):
            # 确定连接符号和前缀
            if level == 0:
                # 根级目录的直接子项
                connector = ""
                new_prefix = "    "
            else:
                if i == len(items) - 1:
                    # 最后一项
                    connector = "└── "
                    new_prefix = prefix + "    "
                else:
                    # 非最后一项
                    connector = "├── "
                    new_prefix = prefix + "│   "
            
            # 添加当前项
            item_marker = "[D] " if item["type"] == "directory" else "[F] "
            output_line = prefix + connector + item_marker + item["name"]
            
            # 如果有错误信息，添加错误标记
            if "error" in item:
                output_line += f"  [ERROR: {item['error']}]"
            
            output.append(output_line)
            
            # 递归格式化子项
            if "children" in item and item["children"]:
                output.extend(_format_tree(item["children"], level + 1, new_prefix))
        
        return output
    
    # 开始格式化
    formatted_lines = [f"目录树: {path} (最大深度: {result['max_depth']})"]
    formatted_lines.extend(_format_tree(result["tree"]))
    formatted_lines.append("")
    formatted_lines.append(f"统计信息:")
    formatted_lines.append(f"  目录数: {result['directories']}")
    formatted_lines.append(f"  文件数: {result['files']}")
    formatted_lines.append(f"  总计: {result['total']}")
    
    return "\n".join(formatted_lines)

if __name__ == "__main__":
    # 示例用法
    # 请将路径替换为您系统上的有效绝对路径
    import tempfile
    temp_dir = tempfile.gettempdir()
    
    # 测试成功情况
    print("测试成功情况 (默认深度3):")
    print(tree_tool_formatted(path=temp_dir))
    
    # 测试指定深度
    print("\n测试指定深度1:")
    print(tree_tool_formatted(path=temp_dir, max_depth=1))
    
    # 测试相对路径错误
    print("\n测试相对路径错误:")
    print(tree_tool_formatted(path="./relative/path"))
    
    # 测试不存在的路径错误
    print("\n测试不存在的路径错误:")
    print(tree_tool_formatted(path="/this/path/does/not/exist/9999"))