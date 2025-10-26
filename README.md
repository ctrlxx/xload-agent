# XLoad Agent 项目

本项目是一个基于VeADK的智能体服务，提供文件系统操作等功能。

## 开发环境安装指南

### 1. 安装uv包管理器

uv是一个现代化的Python包管理器，提供更快的依赖安装体验。请按照以下步骤安装：

```bash
# macOS (使用Homebrew)
brew install uv

# 或者使用pip安装
pip install uv
```

### 2. 安装项目依赖

在项目根目录下执行以下命令，安装完整的Python环境及所有依赖项：

```bash
uv sync --all-extras
```

## 调试与开发启动说明

安装完成后，可以通过以下命令启动开发环境进行调试和开发：

```bash
veadk web
```

启动后，您可以在浏览器中访问相应的URL进行项目调试和开发工作。

## 配置说明

项目配置文件为`config.yaml`，您可以根据需要修改配置参数，包括工作空间路径等设置。

## 注意事项

- 请确保您的Python版本与项目要求兼容（建议使用项目根目录中的`.python-version`指定的Python版本）
- 在开发过程中，如有任何问题，请检查依赖是否正确安装
