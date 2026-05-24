"""
AI Gateway测试项目的pytest配置和fixtures
"""
import os
import pytest
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    config_path = os.getenv("TEST_CONFIG_PATH", "config/test_config.yaml")
    config = load_config(config_path)
    logger.info(f"加载测试配置: {config_path}")
    return config


@pytest.fixture(scope="session")
def gateway_url(test_config):
    """网关URL fixture，支持环境变量 GATEWAY_URL 覆盖"""
    url = os.getenv("GATEWAY_URL") or test_config.get("gateway", {}).get("url", "http://localhost:8080")
    logger.info(f"网关URL: {url}")
    return url


@pytest.fixture(scope="session")
def api_key(test_config):
    """API密钥 fixture，支持环境变量 GATEWAY_API_KEY 覆盖"""
    api_key = os.getenv("GATEWAY_API_KEY") or test_config.get("gateway", {}).get("api_key", "test-api-key")
    return api_key


@pytest.fixture(scope="session")
def mock_config():
    """Mock服务器配置fixture"""
    config_path = os.getenv("MOCK_CONFIG_PATH", "config/mock_config.yaml")
    config = load_config(config_path)
    logger.info(f"加载Mock配置: {config_path}")
    return config


@pytest.fixture(scope="session")
def mock_servers(mock_config):
    """启动Mock服务器"""
    from mock.common_server import MockServerManager

    manager = MockServerManager(mock_config)
    manager.start_all()
    logger.info("Mock服务器已启动")

    yield manager

    manager.stop_all()
    logger.info("Mock服务器已停止")


@pytest.fixture(scope="function")
def http_client(gateway_url, api_key):
    """HTTP客户端fixture"""
    from utils.http_client import GatewayHttpClient

    client = GatewayHttpClient(
        base_url=gateway_url,
        api_key=api_key,
        timeout=30
    )

    yield client

    client.close()


@pytest.fixture(scope="session")
def performance_config(test_config):
    """性能测试配置fixture"""
    return test_config.get("performance", {})


@pytest.fixture(scope="session")
def e2e_config(test_config):
    """E2E测试配置fixture"""
    return test_config.get("e2e", {})


@pytest.fixture(autouse=True)
def log_test_name(request):
    """记录测试名称"""
    logger.info(f"开始测试: {request.node.name}")
    yield
    logger.info(f"结束测试: {request.node.name}")


@pytest.fixture(scope="session")
def allure_environment(test_config):
    """Allure报告环境信息"""
    return {
        "gateway_url": test_config.get("gateway", {}).get("url", "http://localhost:8080"),
        "python_version": os.sys.version,
        "test_environment": os.getenv("TEST_ENV", "local"),
    }