"""
HTTP客户端工具类
"""
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GatewayHttpClient:
    """AI Gateway HTTP客户端"""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        初始化HTTP客户端

        Args:
            base_url: 网关基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def close(self):
        """关闭HTTP客户端"""
        self.session.close()

    def chat_completion(self, request_data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送聊天补全请求

        Args:
            request_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/chat/completions"
        return self._post(url, request_data, **kwargs)

    def chat_completion_stream(self, request_data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送流式聊天补全请求

        Args:
            request_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/chat/completions"
        request_data["stream"] = True
        return self._post(url, request_data, stream=True, **kwargs)

    def embedding(self, request_data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送文本嵌入请求

        Args:
            request_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/embeddings"
        return self._post(url, request_data, **kwargs)

    def image_generation(self, request_data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送图像生成请求

        Args:
            request_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/images/generations"
        return self._post(url, request_data, **kwargs)

    def responses(self, request_data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送Responses请求

        Args:
            request_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/responses"
        return self._post(url, request_data, **kwargs)

    def responses_stream(self, request_data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送流式Responses请求

        Args:
            request_data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/responses"
        request_data["stream"] = True
        return self._post(url, request_data, stream=True, **kwargs)

    def model_list(self, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        获取模型列表

        Args:
            params: 查询参数
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/v1/models"
        return self._get(url, params=params, **kwargs)

    def health_check(self, **kwargs) -> requests.Response:
        """
        健康检查

        Args:
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        url = f"{self.base_url}/health"
        return self._get(url, **kwargs)

    def _post(self, url: str, data: Dict[str, Any], **kwargs) -> requests.Response:
        """
        发送POST请求

        Args:
            url: 请求URL
            data: 请求数据
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        timeout = kwargs.pop("timeout", self.timeout)

        try:
            logger.debug(f"POST {url} - 数据: {data}")
            response = self.session.post(url, json=data, timeout=timeout, **kwargs)
            logger.debug(f"响应状态码: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """
        发送GET请求

        Args:
            url: 请求URL
            params: 查询参数
            **kwargs: 其他请求参数

        Returns:
            响应对象
        """
        timeout = kwargs.pop("timeout", self.timeout)

        try:
            logger.debug(f"GET {url} - 参数: {params}")
            response = self.session.get(url, params=params, timeout=timeout, **kwargs)
            logger.debug(f"响应状态码: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise