"""
文本嵌入接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("文本嵌入接口")
class TestEmbedding:
    """文本嵌入接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_embedding_normal(self, http_client, e2e_config):
        """测试文本嵌入接口正常流程"""
        models = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "input": "Hello world"
                }

                response = http_client.embedding(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert len(data["data"]) > 0
                assert "embedding" in data["data"][0]
                assert isinstance(data["data"][0]["embedding"], list)
                assert len(data["data"][0]["embedding"]) > 0

    @allure.story("批量嵌入")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    def test_embedding_batch(self, http_client, e2e_config):
        """测试文本嵌入接口批量处理"""
        models = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])
        texts = e2e_config.get("test_data", {}).get("embedding_texts", ["Hello world"])

        for model in models:
            with allure.step(f"测试模型: {model}"):
                request_data = {
                    "model": model,
                    "input": texts
                }

                response = http_client.embedding(request_data)

                # 验证响应
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert len(data["data"]) == len(texts)

                # 验证每个嵌入向量
                for i, embedding_data in enumerate(data["data"]):
                    assert "embedding" in embedding_data
                    assert isinstance(embedding_data["embedding"], list)
                    assert len(embedding_data["embedding"]) > 0
                    assert embedding_data["index"] == i

    @allure.story("边界条件")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_embedding_boundary(self, http_client, e2e_config):
        """测试文本嵌入接口边界条件"""
        model = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])[0]

        # 测试空输入
        with allure.step("测试空输入"):
            request_data = {
                "model": model,
                "input": ""
            }
            response = http_client.embedding(request_data)
            # 根据网关配置，可能返回400或200
            assert response.status_code in [200, 400]

        # 测试超长文本
        with allure.step("测试超长文本"):
            long_text = "Hello " * 10000
            request_data = {
                "model": model,
                "input": long_text
            }
            response = http_client.embedding(request_data)
            # 根据网关配置，可能返回400或200
            assert response.status_code in [200, 400]

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_embedding_error_handling(self, http_client):
        """测试文本嵌入接口错误处理"""
        # 测试无效模型
        with allure.step("测试无效模型"):
            request_data = {
                "model": "invalid-model",
                "input": "Hello world"
            }
            response = http_client.embedding(request_data)
            assert response.status_code in [400, 404]

        # 测试无效请求体
        with allure.step("测试无效请求体"):
            request_data = {
                "model": "text-embedding-ada-002"
                # 缺少input字段
            }
            response = http_client.embedding(request_data)
            assert response.status_code == 400

    @allure.story("网关特性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_embedding_gateway_features(self, http_client, e2e_config):
        """测试文本嵌入接口网关特性"""
        model = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])[0]

        # 测试不同维度的嵌入
        with allure.step("测试不同维度的嵌入"):
            request_data = {
                "model": model,
                "input": "Hello world",
                "dimensions": 512
            }
            response = http_client.embedding(request_data)
            # 根据网关配置，可能支持或不支持dimensions参数
            assert response.status_code in [200, 400]

        # 测试编码格式
        with allure.step("测试编码格式"):
            request_data = {
                "model": model,
                "input": "Hello world",
                "encoding_format": "float"
            }
            response = http_client.embedding(request_data)
            assert response.status_code == 200