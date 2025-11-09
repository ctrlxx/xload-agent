from typing import Optional, Dict

from google.adk.tools.tool_context import ToolContext

from .bash_terminal import BashTerminal

from xload_agent.config import Config

config = Config()

keep_alive_terminal: BashTerminal | None = None


def bash_tool(
    command: str,
    reset_cwd: Optional[bool] = False,
    tool_context: ToolContext = None
) -> Dict:
    """在保持活动状态的shell中执行标准bash命令，并在成功时返回输出或在失败时返回错误消息。

    使用此工具执行以下操作：
    - 创建目录
    - 安装依赖项
    - 启动开发服务器
    - 运行测试和代码检查
    - Git操作

    切勿使用此工具执行任何有害或危险的操作。

    - 对于文件系统操作，请使用`ls`、`grep`、`tree`和`k6`工具代替此工具。
    - 使用`text_editor`工具和`create`命令创建新文件。

    Args:
        command: 要执行的命令。
        reset_cwd: 是否将当前工作目录重置为项目根目录。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        dict: 包含执行结果的字典，格式为{"status": "success", "output": "输出内容"} 
             或错误信息{"status": "error", "message": "错误描述"}
    """
    global keep_alive_terminal
    
    # 获取项目根目录（如果tool_context可用）
    project_workspace = None
    if tool_context:
        # 从当前文件路径动态计算项目根目录
        project_workspace = config.workspace_path
    
    try:
        # 初始化或重置终端
        if keep_alive_terminal is None:
            keep_alive_terminal = BashTerminal(project_workspace)
        elif reset_cwd:
            keep_alive_terminal.close()
            keep_alive_terminal = BashTerminal(project_workspace)
        
        # 执行命令
        output = keep_alive_terminal.execute(command)
        
        return {
            "status": "success",
            "command": command,
            "output": output
        }
        
    except Exception as e:
        return {
            "status": "error",
            "command": command,
            "message": f"执行命令时出错: {str(e)}"
        }


def bash_tool_formatted(
    command: str,
    reset_cwd: Optional[bool] = False,
    tool_context: ToolContext = None
) -> str:
    """在保持活动状态的shell中执行标准bash命令，并返回格式化的输出结果。

    使用此工具执行以下操作：
    - 创建目录
    - 安装依赖项
    - 启动开发服务器
    - 运行测试和代码检查
    - Git操作

    切勿使用此工具执行任何有害或危险的操作。

    - 对于文件系统操作，请使用`ls`、`grep`和`tree`工具代替此工具。
    - 使用`text_editor`工具和`create`命令创建新文件。

    Args:
        command: 要执行的命令。
        reset_cwd: 是否将当前工作目录重置为项目根目录。
        tool_context: 工具上下文，由google-adk自动提供。

    Returns:
        str: 格式化的执行结果或错误消息。
    """
    result = bash_tool(command, reset_cwd, tool_context)
    
    if result["status"] == "error":
        return f"错误执行命令 `{result['command']}`:\n```\n{result['message']}\n```"
    
    # 格式化成功结果
    output_lines = []
    output_lines.append(f"命令执行成功: `{result['command']}`")
    output_lines.append("\n输出结果:")
    output_lines.append(f"```\n{result['output']}\n```")
    
    return '\n'.join(output_lines)


# 示例用法
if __name__ == "__main__":
    # 测试简单命令
    print("测试1: 执行 'pwd' 命令")
    print(bash_tool_formatted("pwd"))
    print("\n" + "="*80 + "\n")
    
    # 测试列出目录内容
    print("测试2: 执行 'ls -la' 命令")
    print(bash_tool_formatted("ls -la"))
    print("\n" + "="*80 + "\n")
    
    # 测试切换目录
    print("测试3: 执行 'cd .. && pwd' 命令")
    print(bash_tool_formatted("cd .. && pwd"))
    print("\n" + "="*80 + "\n")
    
    # 测试重置工作目录
    print("测试4: 测试重置工作目录")
    print(bash_tool_formatted("pwd", reset_cwd=True))
    print("\n" + "="*80 + "\n")
    
    # 测试错误命令
    print("测试5: 执行错误命令 'nonexistent_command'")
    print(bash_tool_formatted("nonexistent_command"))