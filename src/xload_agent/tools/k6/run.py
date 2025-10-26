import os
import subprocess
import json
import tempfile
from typing import Dict, Any, Optional


def k6_tool(
    script_path: str,
    options: Optional[Dict[str, Any]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    format: str = "json"
) -> Dict[str, Any]:
    """
    执行k6脚本，支持性能测试和负载测试
    
    Args:
        script_path: k6脚本文件路径（必须是绝对路径）
        options: k6执行选项，如vus、duration、iterations等
        env_vars: 环境变量字典
        format: 输出格式，支持json、csv
        
    Returns:
        Dict: 包含执行结果的字典
            - success: 执行是否成功
            - data: 执行结果数据
            - error: 错误信息（如果有）
            - stats: 性能统计信息
    """
    # 验证路径是否为绝对路径
    if not os.path.isabs(script_path):
        return {
            "success": False,
            "data": None,
            "error": f"路径必须是绝对路径: {script_path}",
            "stats": None
        }
    
    # 验证脚本文件是否存在
    if not os.path.isfile(script_path):
        return {
            "success": False,
            "data": None,
            "error": f"脚本文件不存在: {script_path}",
            "stats": None
        }
    
    # 验证文件扩展名是否为.js或.ts
    if not (script_path.endswith('.js') or script_path.endswith('.ts')):
        return {
            "success": False,
            "data": None,
            "error": f"不支持的脚本文件格式，只支持.js或.ts: {script_path}",
            "stats": None
        }
    
    # 检查k6是否安装
    try:
        subprocess.run(["k6", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        return {
            "success": False,
            "data": None,
            "error": "k6未安装或不在PATH中",
            "stats": None
        }
    
    # 构建k6命令
    cmd = ["k6", "run"]
    
    # 添加选项
    if options:
        for key, value in options.items():
            if value is not None:
                cmd.extend([f"--{key}", str(value)])
    
    # 设置环境变量
    process_env = os.environ.copy()
    if env_vars:
        process_env.update(env_vars)
    
    try:
        # 创建临时文件存储输出
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name
        
        # 设置输出格式和输出文件
        if format == "json":
            cmd.extend(["--out", f"json={temp_file_path}"])
        elif format == "csv":
            cmd.extend(["--out", f"csv={temp_file_path}"])
        
        # 添加脚本路径
        cmd.append(script_path)
        
        # 执行k6命令
        result = subprocess.run(
            cmd,
            env=process_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 读取结果
        output = {}
        stats = None
        
        try:
            if os.path.exists(temp_file_path):
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    if format == "json":
                        try:
                            output = json.load(f)
                        except json.JSONDecodeError:
                            output = {"raw_output": f.read()}
                    else:
                        output = {"raw_output": f.read()}
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
        
        # 提取统计信息
        if format == "json" and isinstance(output, dict):
            stats = output.get('stats', {})
        
        # 检查是否成功执行
        success = result.returncode == 0
        
        return {
            "success": success,
            "data": output,
            "error": result.stderr if not success else None,
            "stats": stats,
            "stdout": result.stdout
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"执行k6脚本时出错: {str(e)}",
            "stats": None
        }


def k6_tool_formatted(
    script_path: str,
    options: Optional[Dict[str, Any]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    format: str = "json"
) -> str:
    """
    执行k6脚本并返回格式化的输出结果
    
    Args:
        script_path: k6脚本文件路径
        options: k6执行选项
        env_vars: 环境变量字典
        format: 输出格式
        
    Returns:
        str: 格式化的输出字符串
    """
    result = k6_tool(script_path, options, env_vars, format)
    
    if not result["success"]:
        return f"错误: {result['error']}"
    
    output_lines = []
    output_lines.append(f"✅ k6脚本执行成功: {os.path.basename(script_path)}")
    
    # 添加选项信息
    if options:
        output_lines.append("\n执行选项:")
        for key, value in options.items():
            output_lines.append(f"  - {key}: {value}")
    
    # 添加统计信息
    if result["stats"]:
        output_lines.append("\n性能统计:")
        # 提取主要指标
        http_reqs = result["stats"].get("http_req", {})
        if http_reqs:
            output_lines.append("\nHTTP请求:")
            output_lines.append(f"  - 总数: {http_reqs.get('count', 'N/A')}")
            output_lines.append(f"  - RPS: {http_reqs.get('rate', 'N/A'):.2f}")
            output_lines.append(f"  - 最小响应时间: {http_reqs.get('min', 'N/A'):.2f}ms")
            output_lines.append(f"  - 最大响应时间: {http_reqs.get('max', 'N/A'):.2f}ms")
            output_lines.append(f"  - 平均响应时间: {http_reqs.get('avg', 'N/A'):.2f}ms")
            output_lines.append(f"  - 中位数响应时间: {http_reqs.get('med', 'N/A'):.2f}ms")
            output_lines.append(f"  - 95th百分位: {http_reqs.get('p(95)', 'N/A'):.2f}ms")
            output_lines.append(f"  - 99th百分位: {http_reqs.get('p(99)', 'N/A'):.2f}ms")
        
        # 检查错误率
        checks = result["stats"].get("check", {})
        if checks:
            output_lines.append("\n检查结果:")
            output_lines.append(f"  - 通过率: {checks.get('rate', 'N/A') * 100:.2f}%")
        
        # 提取vus信息
        vus = result["stats"].get("vus", {})
        if vus:
            output_lines.append("\n虚拟用户:")
            output_lines.append(f"  - 活跃: {vus.get('value', 'N/A')}")
    
    # 添加标准输出的一部分
    if result["stdout"]:
        stdout_lines = result["stdout"].split('\n')
        output_lines.append("\nk6输出摘要:")
        # 只显示最后10行作为摘要
        for line in stdout_lines[-10:]:
            if line.strip():
                output_lines.append(f"  {line}")
    
    return '\n'.join(output_lines)


# 示例用法
if __name__ == "__main__":
    # 测试成功执行
    # 注意：这里使用一个不存在的脚本作为示例，实际使用时需要替换为真实的k6脚本路径
    test_script = os.path.join(os.path.dirname(__file__), "test_script.js")
    
    # 如果测试脚本不存在，创建一个简单的测试脚本
    if not os.path.exists(test_script):
        with open(test_script, 'w') as f:
            f.write('''
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

export default function() {
  const res = http.get('https://httpbin.org/get');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
''')
        print(f"已创建测试脚本: {test_script}")
    
    # 测试执行k6脚本
    print("\n=== 测试k6工具 ===\n")
    print(k6_tool_formatted(
        test_script,
        options={"vus": 3, "duration": "5s"}
    ))
    
    # 测试错误处理 - 相对路径
    print("\n=== 测试相对路径错误 ===\n")
    print(k6_tool_formatted("relative/path/to/script.js"))
    
    # 测试错误处理 - 不存在的文件
    print("\n=== 测试不存在的文件 ===\n")
    print(k6_tool_formatted("/path/to/nonexistent/script.js"))