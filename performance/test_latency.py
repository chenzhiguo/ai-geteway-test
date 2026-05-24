"""
延迟性能测试
"""
import pytest
import allure
import time
import statistics
from typing import Dict, Any, List


@allure.epic("AI Gateway")
@allure.feature("性能测试")
@allure.story("延迟测试")
class TestLatency:
    """延迟测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, performance_config):
        """设置测试环境"""
        self.config = performance_config.get("latency", {})
        self.target_p50_ms = self.config.get("target_p50_ms", 200)
        self.target_p95_ms = self.config.get("target_p95_ms", 500)
        self.target_p99_ms = self.config.get("target_p99_ms", 1000)

    @pytest.mark.performance
    def test_chat_completion_latency(self, http_client, e2e_config):
        """测试聊天补全接口延迟"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "stream": False
        }

        results = self._run_latency_test(
            http_client.chat_completion,
            request_data,
            "chat_completion"
        )

        # 验证结果
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_embedding_latency(self, http_client, e2e_config):
        """测试文本嵌入接口延迟"""
        model = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])[0]

        request_data = {
            "model": model,
            "input": "Hello world"
        }

        results = self._run_latency_test(
            http_client.embedding,
            request_data,
            "embedding"
        )

        # 验证结果
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_model_list_latency(self, http_client):
        """测试模型列表接口延迟"""
        results = self._run_latency_test(
            lambda: http_client.model_list(),
            None,
            "model_list"
        )

        # 验证结果
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_stream_latency(self, http_client, e2e_config):
        """测试流式响应延迟"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Tell me a short story"}
            ],
            "stream": True
        }

        results = self._run_stream_latency_test(
            http_client.chat_completion_stream,
            request_data,
            "stream_chat"
        )

        # 验证结果
        assert results["ttft_ms"] <= self.target_p50_ms  # 首字节时间
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms

    def _run_latency_test(self, request_func, request_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """运行延迟测试"""
        results = {
            "response_times": [],
            "successful_requests": 0,
            "failed_requests": 0,
            "total_requests": 100  # 测试100个请求
        }

        with allure.step(f"运行{test_name}延迟测试"):
            for i in range(results["total_requests"]):
                try:
                    start_time = time.time()

                    if request_data:
                        response = request_func(request_data)
                    else:
                        response = request_func()

                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # 转换为毫秒

                    results["response_times"].append(response_time)

                    if response.status_code == 200:
                        results["successful_requests"] += 1
                    else:
                        results["failed_requests"] += 1

                except Exception as e:
                    results["failed_requests"] += 1

            # 计算延迟统计
            if results["response_times"]:
                results["avg_ms"] = statistics.mean(results["response_times"])
                results["p50_ms"] = statistics.median(results["response_times"])
                results["p95_ms"] = self._percentile(results["response_times"], 95)
                results["p99_ms"] = self._percentile(results["response_times"], 99)
                results["min_ms"] = min(results["response_times"])
                results["max_ms"] = max(results["response_times"])
                results["std_dev_ms"] = statistics.stdev(results["response_times"]) if len(results["response_times"]) > 1 else 0

            # 记录到Allure报告
            allure.attach(
                f"总请求数: {results['total_requests']}\n"
                f"成功请求数: {results['successful_requests']}\n"
                f"失败请求数: {results['failed_requests']}\n"
                f"平均延迟: {results.get('avg_ms', 0):.2f}ms\n"
                f"P50延迟: {results.get('p50_ms', 0):.2f}ms\n"
                f"P95延迟: {results.get('p95_ms', 0):.2f}ms\n"
                f"P99延迟: {results.get('p99_ms', 0):.2f}ms\n"
                f"最小延迟: {results.get('min_ms', 0):.2f}ms\n"
                f"最大延迟: {results.get('max_ms', 0):.2f}ms\n"
                f"标准差: {results.get('std_dev_ms', 0):.2f}ms",
                name=f"{test_name}延迟测试结果",
                attachment_type=allure.attachment_type.TEXT
            )

        return results

    def _run_stream_latency_test(self, request_func, request_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """运行流式响应延迟测试"""
        results = {
            "ttft_times": [],  # 首字节时间
            "total_times": [],  # 总响应时间
            "successful_requests": 0,
            "failed_requests": 0,
            "total_requests": 50  # 测试50个流式请求
        }

        with allure.step(f"运行{test_name}流式延迟测试"):
            for i in range(results["total_requests"]):
                try:
                    start_time = time.time()

                    response = request_func(request_data)

                    # 读取第一个chunk
                    first_chunk_time = None
                    for chunk in response.iter_lines():
                        if chunk:
                            first_chunk_time = time.time()
                            break

                    end_time = time.time()

                    if first_chunk_time:
                        ttft = (first_chunk_time - start_time) * 1000
                        results["ttft_times"].append(ttft)

                    total_time = (end_time - start_time) * 1000
                    results["total_times"].append(total_time)

                    if response.status_code == 200:
                        results["successful_requests"] += 1
                    else:
                        results["failed_requests"] += 1

                except Exception as e:
                    results["failed_requests"] += 1

            # 计算延迟统计
            if results["ttft_times"]:
                results["ttft_ms"] = statistics.mean(results["ttft_times"])
                results["ttft_p50_ms"] = statistics.median(results["ttft_times"])
                results["ttft_p95_ms"] = self._percentile(results["ttft_times"], 95)

            if results["total_times"]:
                results["avg_ms"] = statistics.mean(results["total_times"])
                results["p50_ms"] = statistics.median(results["total_times"])
                results["p95_ms"] = self._percentile(results["total_times"], 95)
                results["p99_ms"] = self._percentile(results["total_times"], 99)

            # 记录到Allure报告
            allure.attach(
                f"总请求数: {results['total_requests']}\n"
                f"成功请求数: {results['successful_requests']}\n"
                f"失败请求数: {results['failed_requests']}\n"
                f"平均首字节时间: {results.get('ttft_ms', 0):.2f}ms\n"
                f"P50首字节时间: {results.get('ttft_p50_ms', 0):.2f}ms\n"
                f"P95首字节时间: {results.get('ttft_p95_ms', 0):.2f}ms\n"
                f"平均总时间: {results.get('avg_ms', 0):.2f}ms\n"
                f"P50总时间: {results.get('p50_ms', 0):.2f}ms\n"
                f"P95总时间: {results.get('p95_ms', 0):.2f}ms\n"
                f"P99总时间: {results.get('p99_ms', 0):.2f}ms",
                name=f"{test_name}流式延迟测试结果",
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