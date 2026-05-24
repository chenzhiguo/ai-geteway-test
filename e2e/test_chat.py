"""
聊天补全接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("聊天补全接口")
class TestChatCompletion:
    """聊天补全接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_chat_completion_normal(self, http_client, e2e_config):
        """测试聊天补全接口正常流程"""
        models = e2e_config.get("models", {}).get("chat", ["gpt-4"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "stream": False
                }

                response = http_client.chat_completion(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "choices" in data
                assert len(data["choices"]) > 0
                assert "message" in data["choices"][0]
                assert "content" in data["choices"][0]["message"]
                assert data["model"] == model

    @allure.story("流式响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_chat_completion_stream(self, http_client, e2e_config):
        """测试聊天补全接口流式响应"""
        models = e2e_config.get("models", {}).get("chat", ["gpt-4"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Tell me a short story"}
                    ],
                    "stream": True
                }

                response = http_client.chat_completion_stream(request_data)

                # 验证流式响应
                assert response.status_code == 200
                chunks = []
                for chunk in response.iter_lines():
                    if chunk:
                        chunks.append(chunk)

                assert len(chunks) > 0

    @allure.story("边界条件")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_chat_completion_boundary(self, http_client, e2e_config):
        """测试聊天补全接口边界条件"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4"])[0]

        # 测试空消息
        with allure.step("测试空消息"):
            request_data = {
                "model": model,
                "messages": [],
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            assert response.status_code == 400

        # 测试超长消息
        with allure.step("测试超长消息"):
            long_content = "Hello " * 10000
            request_data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": long_content}
                ],
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            # 根据网关配置，可能返回400或200
            assert response.status_code in [200, 400]

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_chat_completion_error_handling(self, http_client):
        """测试聊天补全接口错误处理"""
        # 测试无效模型
        with allure.step("测试无效模型"):
            request_data = {
                "model": "invalid-model",
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            assert response.status_code in [400, 404]

        # 测试无效请求体
        with allure.step("测试无效请求体"):
            request_data = {
                "model": "gpt-4",
                # 缺少messages字段
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            assert response.status_code == 400

    @allure.story("网关特性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_chat_completion_gateway_features(self, http_client, e2e_config):
        """测试聊天补全接口网关特性"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4"])[0]

        # 测试多个消息
        with allure.step("测试多个消息"):
            request_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                    {"role": "user", "content": "How are you?"}
                ],
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            assert response.status_code == 200

        # 测试温度参数
        with allure.step("测试温度参数"):
            request_data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "temperature": 0.7,
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            assert response.status_code == 200

        # 测试最大令牌数
        with allure.step("测试最大令牌数"):
            request_data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "max_tokens": 100,
                "stream": False
            }
            response = http_client.chat_completion(request_data)
            assert response.status_code == 200