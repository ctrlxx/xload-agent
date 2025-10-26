import yaml
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent.parent.absolute()


class Config:
    """配置管理类，从config.yaml读取配置"""
    
    def __init__(self):
        self.config_path = ROOT_DIR / 'config.yaml'
        self._config_data = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: config.yaml not found at {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing config.yaml: {e}")
            return {}
    
    def get(self, key_path, default=None):
        """
        获取配置项
        key_path: 配置路径，支持点号分隔，如 'model.agent.name'
        """
        keys = key_path.split('.')
        value = self._config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @property
    def model(self):
        """获取模型配置"""
        return self._config_data.get('model', {})
    
    @property
    def volcengine(self):
        """获取火山引擎配置"""
        return self._config_data.get('volcengine', {})
    
    @property
    def observability(self):
        """获取可观察性配置"""
        return self._config_data.get('observability', {})
    
    @property
    def database(self):
        """获取数据库配置"""
        return self._config_data.get('database', {})
    
    @property
    def logging_level(self):
        """获取日志级别"""
        return self._config_data.get('logging', {}).get('level', 'INFO')
    
    @property
    def workspace_path(self) -> str:
        """获取工作空间配置"""
        return self._config_data.get('project', {}).get('workspace', {}).get('path', '/tmp')


# 创建全局配置实例
init_config = Config()

# 导出常用配置项
MODEL_AGENT_NAME = init_config.get('model.agent.name')
MODEL_AGENT_API_BASE = init_config.get('model.agent.api_base')
MODEL_AGENT_API_KEY = init_config.get('model.agent.api_key')
VOLCENGINE_ACCESS_KEY = init_config.get('volcengine.access_key')
VOLCENGINE_SECRET_KEY = init_config.get('volcengine.secret_key')

XLOAD_WORKSPACE = init_config.get('project.workspace.path')

LOGGING_LEVEL = init_config.logging_level

if __name__ == '__main__':
    print(init_config.workspace_path)
