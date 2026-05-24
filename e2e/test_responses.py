"""
OpenAI Responses接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("Responses接口")
class TestResponses:
    """Responses接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_responses_normal(self, http_client, e2e_config):
        """测试Responses接口正常流程"""
        models = e2e_config.get("models", {}).get("responses", ["gpt-4"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "input": "Hello, how are you?",
                    "stream": False
                }

                response = http_client.responses(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "output" in data
                assert len(data["output"]) > 0
                assert "content" in data["output"][0]
                assert data["model"] == model

    @allure.story("流式响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_responses_stream(self, http_client, e2e_config):
        """测试Responses接口流式响应"""
        models = e2e_config.get("models", {}).get("responses", ["gpt-4"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "input": "Tell me a short story",
                    "stream": True
                }

                response = http_client.responses_stream(request_data)

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
    def test_responses_multi_turn(self, http_client, e2e_config):
        """测试Responses接口多轮对话"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "input": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ],
            "stream": False
        }

        response = http_client.responses(request_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "output" in data
        assert len(data["output"]) > 0

    @allure.story("边界条件")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_responses_boundary(self, http_client, e2e_config):
        """测试Responses接口边界条件"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        # 测试空输入
        with allure.step("测试空输入"):
            request_data = {
                "model": model,
                "input": "",
                "stream": False
            }
            response = http_client.responses(request_data)
            assert response.status_code == 400

        # 测试超长输入
        with allure.step("测试超长输入"):
            long_input = "Hello " * 10000
            request_data = {
                "model": model,
                "input": long_input,
                "stream": False
            }
            response = http_client.responses(request_data)
            # 根据网关配置，可能返回400或200
            assert response.status_code in [200, 400]

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_responses_error_handling(self, http_client):
        """测试Responses接口错误处理"""
        # 测试无效模型
        with allure.step("测试无效模型"):
            request_data = {
                "model": "invalid-model",
                "input": "Hello",
                "stream": False
            }
            response = http_client.responses(request_data)
            assert response.status_code in [400, 404]

        # 测试无效请求体
        with allure.step("测试无效请求体"):
            request_data = {
                "model": "gpt-4"
                # 缺少input字段
            }
            response = http_client.responses(request_data)
            assert response.status_code == 400

    @allure.story("网关特性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_responses_gateway_features(self, http_client, e2e_config):
        """测试Responses接口网关特性"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        # 测试温度参数
        with allure.step("测试温度参数"):
            request_data = {
                "model": model,
                "input": "Hello",
                "temperature": 0.7,
                "stream": False
            }
            response = http_client.responses(request_data)
            assert response.status_code == 200

        # 测试最大输出令牌数
        with allure.step("测试最大输出令牌数"):
            request_data = {
                "model": model,
                "input": "Hello",
                "max_output_tokens": 100,
                "stream": False
            }
            response = http_client.responses(request_data)
            assert response.status_code == 200

        # 测试工具调用
        with allure.step("测试工具调用"):
            request_data = {
                "model": model,
                "input": "What is the weather?",
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "description": "Get the weather",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string"}
                                }
                            }
                        }
                    }
                ],
                "stream": False
            }
            response = http_client.responses(request_data)
            # 根据网关配置，可能支持或不支持工具调用
            assert response.status_code in [200, 400]