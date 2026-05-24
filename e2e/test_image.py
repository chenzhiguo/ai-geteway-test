"""
图像生成接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("图像生成接口")
class TestImageGeneration:
    """图像生成接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_image_generation_normal(self, http_client, e2e_config):
        """测试图像生成接口正常流程"""
        models = e2e_config.get("models", {}).get("image", ["dall-e-3"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "prompt": "A beautiful sunset over the ocean",
                    "n": 1,
                    "size": "1024x1024"
                }

                response = http_client.image_generation(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert len(data["data"]) > 0
                assert "url" in data["data"][0]

    @allure.story("不同尺寸")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    def test_image_generation_sizes(self, http_client, e2e_config):
        """测试图像生成接口不同尺寸"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]
        sizes = ["256x256", "512x512", "1024x1024"]

        for size in sizes:
            with allure.step(f"测试尺寸: {size}"):
                request_data = {
                    "model": model,
                    "prompt": "A beautiful sunset",
                    "n": 1,
                    "size": size
                }

                response = http_client.image_generation(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert len(data["data"]) > 0

    @allure.story("多张图片")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    def test_image_generation_multiple(self, http_client, e2e_config):
        """测试图像生成接口多张图片"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]

        request_data = {
            "model": model,
            "prompt": "A beautiful sunset",
            "n": 3,
            "size": "1024x1024"
        }

        response = http_client.image_generation(request_data)

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 3

    @allure.story("边界条件")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_image_generation_boundary(self, http_client, e2e_config):
        """测试图像生成接口边界条件"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]

        # 测试空提示
        with allure.step("测试空提示"):
            request_data = {
                "model": model,
                "prompt": "",
                "n": 1,
                "size": "1024x1024"
            }
            response = http_client.image_generation(request_data)
            assert response.status_code == 400

        # 测试超长提示
        with allure.step("测试超长提示"):
            long_prompt = "A beautiful sunset " * 1000
            request_data = {
                "model": model,
                "prompt": long_prompt,
                "n": 1,
                "size": "1024x1024"
            }
            response = http_client.image_generation(request_data)
            # 根据网关配置，可能返回400或200
            assert response.status_code in [200, 400]

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_image_generation_error_handling(self, http_client):
        """测试图像生成接口错误处理"""
        # 测试无效模型
        with allure.step("测试无效模型"):
            request_data = {
                "model": "invalid-model",
                "prompt": "A beautiful sunset",
                "n": 1,
                "size": "1024x1024"
            }
            response = http_client.image_generation(request_data)
            assert response.status_code in [400, 404]

        # 测试无效尺寸
        with allure.step("测试无效尺寸"):
            request_data = {
                "model": "dall-e-3",
                "prompt": "A beautiful sunset",
                "n": 1,
                "size": "invalid-size"
            }
            response = http_client.image_generation(request_data)
            assert response.status_code == 400

        # 测试无效请求数量
        with allure.step("测试无效请求数量"):
            request_data = {
                "model": "dall-e-3",
                "prompt": "A beautiful sunset",
                "n": 0,
                "size": "1024x1024"
            }
            response = http_client.image_generation(request_data)
            assert response.status_code == 400

    @allure.story("网关特性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_image_generation_gateway_features(self, http_client, e2e_config):
        """测试图像生成接口网关特性"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]

        # 测试不同质量
        with allure.step("测试不同质量"):
            request_data = {
                "model": model,
                "prompt": "A beautiful sunset",
                "n": 1,
                "size": "1024x1024",
                "quality": "hd"
            }
            response = http_client.image_generation(request_data)
            # 根据网关配置，可能支持或不支持quality参数
            assert response.status_code in [200, 400]

        # 测试不同风格
        with allure.step("测试不同风格"):
            request_data = {
                "model": model,
                "prompt": "A beautiful sunset",
                "n": 1,
                "size": "1024x1024",
                "style": "vivid"
            }
            response = http_client.image_generation(request_data)
            # 根据网关配置，可能支持或不支持style参数
            assert response.status_code in [200, 400]