"""
Anthropic Messages接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("Anthropic Messages接口")
class TestAnthropicMessages:
    """Anthropic Messages接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_messages_normal(self, http_client, e2e_config):
        """测试Messages接口正常流程"""
        models = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "max_tokens": 1024
                }

                response = http_client.messages(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert data["type"] == "message"
                assert data["role"] == "assistant"
                assert len(data["content"]) > 0
                assert data["content"][0]["type"] == "text"
                assert data["content"][0]["text"]

    @allure.story("流式响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_messages_stream(self, http_client, e2e_config):
        """测试Messages接口流式响应"""
        models = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Tell me a short story"}
                    ],
                    "max_tokens": 1024,
                    "stream": True
                }

                response = http_client.messages_stream(request_data)

                # 验证流式响应
                assert response.status_code == 200
                chunks = []
                for chunk in response.iter_lines():
                    if chunk:
                        chunks.append(chunk)

                assert len(chunks) > 0

    @allure.story("多轮对话")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_messages_multi_turn(self, http_client, e2e_config):
        """测试Messages接口多轮对话"""
        model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]

        request_data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "What is 2+2?"},
                {"role": "assistant", "content": "2+2 equals 4."},
                {"role": "user", "content": "And 3+3?"}
            ],
            "max_tokens": 1024
        }

        response = http_client.messages(request_data)
        assert response.status_code == 200

    @allure.story("系统提示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_messages_system_prompt(self, http_client, e2e_config):
        """测试Messages接口系统提示"""
        model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]

        request_data = {
            "model": model,
            "system": "You are a helpful assistant that responds in Chinese.",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 1024
        }

        response = http_client.messages(request_data)
        assert response.status_code == 200

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_messages_error_handling(self, http_client):
        """测试Messages接口错误处理"""
        # 测试无效模型
        with allure.step("测试无效模型"):
            request_data = {
                "model": "invalid-model",
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
            response = http_client.messages(request_data)
            assert response.status_code in [400, 404]

        # 测试无效请求体
        with allure.step("测试无效请求体"):
            request_data = {
                "model": "claude-sonnet-4-20250514",
                # 缺少messages字段
            }
            response = http_client.messages(request_data)
            assert response.status_code == 400
