"""
吞吐量性能测试
"""
import pytest
import allure
import time
import statistics
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed


@allure.epic("AI Gateway")
@allure.feature("性能测试")
@allure.story("吞吐量测试")
class TestThroughput:
    """吞吐量测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, performance_config):
        """设置测试环境"""
        self.config = performance_config.get("throughput", {})
        self.target_qps = self.config.get("target_qps", 100)
        self.duration_seconds = self.config.get("duration_seconds", 60)
        self.ramp_up_seconds = self.config.get("ramp_up_seconds", 10)

    @pytest.mark.performance
    def test_chat_completion_throughput(self, http_client, e2e_config):
        """测试聊天补全接口吞吐量"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "stream": False
        }

        results = self._run_throughput_test(
            http_client.chat_completion,
            request_data,
            "chat_completion"
        )

        # 验证结果
        assert results["qps"] >= self.target_qps * 0.8  # 允许20%的误差
        assert results["error_rate"] < 0.01  # 错误率小于1%

    @pytest.mark.performance
    def test_embedding_throughput(self, http_client, e2e_config):
        """测试文本嵌入接口吞吐量"""
        model = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])[0]

        request_data = {
            "model": model,
            "input": "Hello world"
        }

        results = self._run_throughput_test(
            http_client.embedding,
            request_data,
            "embedding"
        )

        # 验证结果
        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

    @pytest.mark.performance
    def test_model_list_throughput(self, http_client):
        """测试模型列表接口吞吐量"""
        results = self._run_throughput_test(
            lambda: http_client.model_list(),
            None,
            "model_list"
        )

        # 验证结果
        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

    def _run_throughput_test(self, request_func, request_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """运行吞吐量测试"""
        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "start_time": None,
            "end_time": None,
            "qps": 0,
            "error_rate": 0
        }

        with allure.step(f"运行{test_name}吞吐量测试"):
            # 记录开始时间
            results["start_time"] = time.time()
            start_time = results["start_time"]

            # 使用线程池执行请求
            with ThreadPoolExecutor(max_workers=self.target_qps) as executor:
                futures = []

                # 提交请求
                while time.time() - start_time < self.duration_seconds:
                    if request_data:
                        future = executor.submit(request_func, request_data)
                    else:
                        future = executor.submit(request_func)
                    futures.append(future)

                    # 控制请求速率
                    time.sleep(1.0 / self.target_qps)

                # 等待所有请求完成
                for future in as_completed(futures):
                    try:
                        response = future.result()
                        results["total_requests"] += 1

                        if response.status_code == 200:
                            results["successful_requests"] += 1
                        else:
                            results["failed_requests"] += 1

                        # 记录响应时间
                        if hasattr(response, 'elapsed'):
                            results["response_times"].append(response.elapsed.total_seconds())

                    except Exception as e:
                        results["total_requests"] += 1
                        results["failed_requests"] += 1

            # 记录结束时间
            results["end_time"] = time.time()
            duration = results["end_time"] - results["start_time"]

            # 计算指标
            if duration > 0:
                results["qps"] = results["total_requests"] / duration

            if results["total_requests"] > 0:
                results["error_rate"] = results["failed_requests"] / results["total_requests"]

            # 计算响应时间统计
            if results["response_times"]:
                results["avg_response_time"] = statistics.mean(results["response_times"])
                results["p50_response_time"] = statistics.median(results["response_times"])
                results["p95_response_time"] = self._percentile(results["response_times"], 95)
                results["p99_response_time"] = self._percentile(results["response_times"], 99)

            # 记录到Allure报告
            allure.attach(
                f"总请求数: {results['total_requests']}\n"
                f"成功请求数: {results['successful_requests']}\n"
                f"失败请求数: {results['failed_requests']}\n"
                f"QPS: {results['qps']:.2f}\n"
                f"错误率: {results['error_rate']:.2%}\n"
                f"平均响应时间: {results.get('avg_response_time', 0):.3f}s\n"
                f"P50响应时间: {results.get('p50_response_time', 0):.3f}s\n"
                f"P95响应时间: {results.get('p95_response_time', 0):.3f}s\n"
                f"P99响应时间: {results.get('p99_response_time', 0):.3f}s",
                name=f"{test_name}吞吐量测试结果",
                attachment_type=allure.attachment_type.TEXT
            )

        return results

    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]