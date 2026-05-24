"""
Google Gemini接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("Google Gemini接口")
class TestGoogleGemini:
    """Google Gemini接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_generate_content_normal(self, http_client, e2e_config):
        """测试内容生成接口正常流程"""
        models = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "contents": [
                        {
                            "parts": [
                                {"text": "Hello, how are you?"}
                            ]
                        }
                    ]
                }

                response = http_client.gemini_generate(model, request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "candidates" in data
                assert len(data["candidates"]) > 0
                assert "content" in data["candidates"][0]
                assert "parts" in data["candidates"][0]["content"]
                assert len(data["candidates"][0]["content"]["parts"]) > 0
                assert data["candidates"][0]["content"]["parts"][0]["text"]

    @allure.story("流式响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_generate_content_stream(self, http_client, e2e_config):
        """测试内容生成接口流式响应"""
        models = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "contents": [
                        {
                            "parts": [
                                {"text": "Tell me a short story"}
                            ]
                        }
                    ]
                }

                response = http_client.gemini_stream(model, request_data)

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
    def test_generate_content_multi_turn(self, http_client, e2e_config):
        """测试内容生成接口多轮对话"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "What is 2+2?"}]
                },
                {
                    "role": "model",
                    "parts": [{"text": "2+2 equals 4."}]
                },
                {
                    "role": "user",
                    "parts": [{"text": "And 3+3?"}]
                }
            ]
        }

        response = http_client.gemini_generate(model, request_data)
        assert response.status_code == 200

    @allure.story("系统指令")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_generate_content_system_instruction(self, http_client, e2e_config):
        """测试内容生成接口系统指令"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "systemInstruction": {
                "parts": [
                    {"text": "You are a helpful assistant that responds in Chinese."}
                ]
            },
            "contents": [
                {
                    "parts": [
                        {"text": "Hello"}
                    ]
                }
            ]
        }

        response = http_client.gemini_generate(model, request_data)
        assert response.status_code == 200

    @allure.story("生成参数")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_generate_content_parameters(self, http_client, e2e_config):
        """测试内容生成接口生成参数"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "contents": [
                {
                    "parts": [
                        {"text": "Hello"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100,
                "topP": 0.9
            }
        }

        response = http_client.gemini_generate(model, request_data)
        assert response.status_code == 200

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_generate_content_error_handling(self, http_client):
        """测试内容生成接口错误处理"""
        # 测试无效模型
        with allure.step("测试无效模型"):
            request_data = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Hello"}
                        ]
                    }
                ]
            }
            response = http_client.gemini_generate("invalid-model", request_data)
            assert response.status_code in [400, 404]

        # 测试无效请求体
        with allure.step("测试无效请求体"):
            request_data = {}  # 缺少contents字段
            response = http_client.gemini_generate("gemini-2.0-flash", request_data)
            assert response.status_code == 400
