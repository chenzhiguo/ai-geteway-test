"""
配置加载器工具类
"""
import os
import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_dir: str = "config"):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_cache: Dict[str, Any] = {}

    def load(self, config_name: str, env_prefix: str = "") -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_name: 配置文件名（不含扩展名）
            env_prefix: 环境变量前缀

        Returns:
            配置字典
        """
        # 检查缓存
        if config_name in self.config_cache:
            return self.config_cache[config_name]

        # 构建配置文件路径
        config_path = self.config_dir / f"{config_name}.yaml"

        # 检查文件是否存在
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}")
            return {}

        # 加载配置文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

            # 处理环境变量替换
            if env_prefix:
                config = self._replace_env_vars(config, env_prefix)

            # 缓存配置
            self.config_cache[config_name] = config
            logger.info(f"加载配置文件: {config_path}")

            return config

        except Exception as e:
            logger.error(f"加载配置文件失败: {config_path} - {e}")
            return {}

    def load_test_config(self) -> Dict[str, Any]:
        """
        加载测试配置

        Returns:
            测试配置字典
        """
        return self.load("test_config", "TEST_")

    def load_mock_config(self) -> Dict[str, Any]:
        """
        加载Mock服务器配置

        Returns:
            Mock服务器配置字典
        """
        return self.load("mock_config", "MOCK_")

    def _replace_env_vars(self, config: Any, env_prefix: str) -> Any:
        """
        替换配置中的环境变量

        Args:
            config: 配置对象
            env_prefix: 环境变量前缀

        Returns:
            替换后的配置对象
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v, env_prefix) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item, env_prefix) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            # 提取环境变量名
            env_var = config[2:-1]
            # 添加前缀
            if env_prefix and not env_var.startswith(env_prefix):
                env_var = f"{env_prefix}{env_var}"
            # 获取环境变量值
            env_value = os.getenv(env_var)
            if env_value is not None:
                logger.debug(f"替换环境变量: {config} -> {env_value}")
                return env_value
            else:
                logger.warning(f"环境变量不存在: {env_var}")
                return config
        else:
            return config

    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            config_name: 配置文件名
            key: 配置键（支持点号分隔的路径）
            default: 默认值

        Returns:
            配置值
        """
        config = self.load(config_name)
        keys = key.split(".")

        # 遍历配置路径
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def clear_cache(self):
        """清除配置缓存"""
        self.config_cache.clear()
        logger.info("配置缓存已清除")