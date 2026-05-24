"""
模型列表接口E2E测试
"""
import pytest
import allure
from typing import Dict, Any


@allure.epic("AI Gateway")
@allure.feature("模型列表接口")
class TestModelList:
    """模型列表接口测试类"""

    @allure.story("正常流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_model_list_normal(self, http_client):
        """测试模型列表接口正常流程"""
        response = http_client.model_list()

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # 验证模型结构
        for model in data["data"]:
            assert "id" in model
            assert "object" in model
            assert model["object"] == "model"

    @allure.story("模型详情")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    def test_model_list_details(self, http_client):
        """测试模型列表接口模型详情"""
        response = http_client.model_list()

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

        # 验证每个模型都有详细信息
        for model in data["data"]:
            assert "id" in model
            assert "object" in model
            assert "created" in model
            assert "owned_by" in model

    @allure.story("过滤功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    def test_model_list_filter(self, http_client):
        """测试模型列表接口过滤功能"""
        # 获取所有模型
        response = http_client.model_list()
        assert response.status_code == 200
        all_models = response.json()["data"]

        # 如果支持过滤，测试过滤功能
        # 注意：这取决于网关是否支持过滤参数
        if len(all_models) > 0:
            # 尝试按owned_by过滤
            owner = all_models[0].get("owned_by", "")
            if owner:
                response = http_client.model_list(params={"owned_by": owner})
                # 根据网关配置，可能支持或不支持过滤
                assert response.status_code in [200, 400]

    @allure.story("边界条件")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_model_list_boundary(self, http_client):
        """测试模型列表接口边界条件"""
        # 测试分页参数（如果支持）
        response = http_client.model_list(params={"limit": 10})
        # 根据网关配置，可能支持或不支持分页
        assert response.status_code in [200, 400]

        # 测试偏移参数（如果支持）
        response = http_client.model_list(params={"offset": 0})
        # 根据网关配置，可能支持或不支持偏移
        assert response.status_code in [200, 400]

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_model_list_error_handling(self, http_client):
        """测试模型列表接口错误处理"""
        # 测试无效参数
        response = http_client.model_list(params={"invalid_param": "value"})
        # 根据网关配置，可能忽略无效参数或返回错误
        assert response.status_code in [200, 400]

    @allure.story("网关特性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.e2e
    @pytest.mark.regression
    def test_model_list_gateway_features(self, http_client, e2e_config):
        """测试模型列表接口网关特性"""
        response = http_client.model_list()

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

        # 验证模型类型
        model_types = set()
        for model in data["data"]:
            if "owned_by" in model:
                model_types.add(model["owned_by"])

        # 验证包含不同提供商的模型
        # 注意：这取决于网关配置的提供商
        assert len(model_types) > 0

        # 验证模型ID格式
        for model in data["data"]:
            model_id = model["id"]
            assert isinstance(model_id, str)
            assert len(model_id) > 0