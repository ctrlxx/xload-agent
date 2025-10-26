import fnmatch
from pathlib import Path
from typing import Optional

from google.adk.tools.tool_context import ToolContext


def ls_tool(
    path: str,
    match: Optional[list[str]] = None,
    ignore: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> dict:
    """列出给定路径中的文件和目录。可以选择性地提供glob模式来匹配和忽略。

    Args:
        path: 要列出文件和目录的绝对路径。不允许使用相对路径。
        match: 可选的glob模式数组，用于匹配文件和目录。
        ignore: 可选的glob模式数组，用于忽略文件和目录。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        dict: 包含列出结果的字典，格式为{"status": "success", "items": [...]}
             或错误信息{"status": "error", "message": "错误描述"}
    """
    # 默认忽略模式
    DEFAULT_IGNORE_PATTERNS = [
        "*.pyc", "__pycache__", "*.swp", ".DS_Store", ".git", ".svn", ".hg",
        "*.tmp", "*.temp", "*.log", ".idea", "*.vscode", "node_modules"
    ]
    
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
    
    # 获取目录中的所有项目
    try:
        items = list(_path.iterdir())
    except PermissionError:
        return {
            "status": "error",
            "message": f"错误: 没有权限访问路径 {path}。"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"错误: 访问路径时发生异常: {str(e)}"
        }
    
    # 排序项目: 目录在前，文件在后，都按字母顺序排列
    items.sort(key=lambda x: (x.is_file(), x.name.lower()))
    
    # 应用匹配模式（如果提供）
    if match:
        filtered_items = []
        for item in items:
            for pattern in match:
                if fnmatch.fnmatch(item.name, pattern):
                    filtered_items.append(item)
                    break
        items = filtered_items
    
    # 应用忽略模式
    ignore = (ignore or []) + DEFAULT_IGNORE_PATTERNS
    filtered_items = []
    for item in items:
        should_ignore = False
        for pattern in ignore:
            if fnmatch.fnmatch(item.name, pattern):
                should_ignore = True
                break
        if not should_ignore:
            filtered_items.append(item)
    items = filtered_items
    
    # 格式化输出项目
    result_items = []
    for item in items:
        if item.is_dir():
            result_items.append(item.name + "/")
        else:
            result_items.append(item.name)
    
    return {
        "status": "success",
        "path": path,
        "items": result_items,
        "count": len(result_items)
    }


def ls_tool_formatted(
    path: str,
    match: Optional[list[str]] = None,
    ignore: Optional[list[str]] = None,
    tool_context: ToolContext = None
) -> str:
    """列出给定路径中的文件和目录，并返回格式化的字符串结果。

    Args:
        path: 要列出文件和目录的绝对路径。不允许使用相对路径。
        match: 可选的glob模式数组，用于匹配文件和目录。
        ignore: 可选的glob模式数组，用于忽略文件和目录。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        str: 格式化的列表结果或错误消息。
    """
    result = ls_tool(path, match, ignore, tool_context)
    
    if result["status"] == "error":
        return result["message"]
    
    if not result["items"]:
        return f"在 {path} 中未找到项目。"
    
    formatted_result = f"在 {path} 中的结果：\n```\n"
    formatted_result += "\n".join(result["items"])
    formatted_result += f"\n```\n共找到 {result['count']} 个项目。"
    
    return formatted_result


if __name__ == "__main__":
    # 示例用法
    # 请将路径替换为您系统上的有效绝对路径
    import tempfile
    temp_dir = tempfile.gettempdir()
    
    # 测试成功情况
    print("测试成功情况:")
    print(ls_tool_formatted(path=temp_dir))
    
    # 测试相对路径错误
    print("\n测试相对路径错误:")
    print(ls_tool_formatted(path="./relative/path"))
    
    # 测试不存在的路径错误
    print("\n测试不存在的路径错误:")
    print(ls_tool_formatted(path="/this/path/does/not/exist/9999"))