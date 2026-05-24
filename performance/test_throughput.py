"""
吞吐量性能测试
"""
import pytest
import allure
import time
import statistics
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from performance.utils import percentile


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

    @pytest.mark.performance
    def test_chat_completion_throughput(self, http_client, e2e_config):
        """测试聊天补全接口吞吐量"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4o"])[0]

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

        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

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

        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

    @pytest.mark.performance
    def test_image_generation_throughput(self, http_client, e2e_config):
        """测试图片生成接口吞吐量"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]

        request_data = {
            "model": model,
            "prompt": "A sunset over a mountain landscape",
            "n": 1,
            "size": "256x256"
        }

        image_qps = self.config.get("image_target_qps", 10)
        results = self._run_throughput_test(
            http_client.image_generation,
            request_data,
            "image_generation",
            target_qps=image_qps
        )

        assert results["qps"] >= image_qps * 0.8
        assert results["error_rate"] < 0.05

    @pytest.mark.performance
    def test_responses_throughput(self, http_client, e2e_config):
        """测试Responses接口吞吐量"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "input": "Hello, how are you?",
            "stream": False
        }

        results = self._run_throughput_test(
            http_client.responses,
            request_data,
            "responses"
        )

        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

    @pytest.mark.performance
    def test_messages_throughput(self, http_client, e2e_config):
        """测试Messages接口吞吐量"""
        model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]

        request_data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "max_tokens": 100
        }

        results = self._run_throughput_test(
            http_client.messages,
            request_data,
            "messages"
        )

        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

    @pytest.mark.performance
    def test_gemini_generate_throughput(self, http_client, e2e_config):
        """测试Gemini生成接口吞吐量"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "contents": [{"parts": [{"text": "Hello, how are you?"}]}]
        }

        results = self._run_throughput_test(
            lambda data: http_client.gemini_generate(model, data),
            request_data,
            "gemini_generate"
        )

        assert results["qps"] >= self.target_qps * 0.8
        assert results["error_rate"] < 0.01

    @pytest.mark.performance
    def test_health_check_throughput(self, http_client):
        """测试健康检查接口吞吐量"""
        health_qps = self.config.get("health_target_qps", 500)
        results = self._run_throughput_test(
            lambda: http_client.health_check(),
            None,
            "health_check",
            target_qps=health_qps
        )

        assert results["qps"] >= health_qps * 0.8
        assert results["error_rate"] < 0.01

    def _run_throughput_test(self, request_func, request_data: Dict[str, Any], test_name: str, target_qps: int = None) -> Dict[str, Any]:
        """运行吞吐量测试"""
        qps = target_qps or self.target_qps
        max_workers = min(qps, 200)

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
            results["start_time"] = time.time()
            start_time = results["start_time"]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                interval = 1.0 / qps

                while time.time() - start_time < self.duration_seconds:
                    if request_data:
                        future = executor.submit(request_func, request_data)
                    else:
                        future = executor.submit(request_func)
                    futures.append(future)

                    time.sleep(interval)

                for future in as_completed(futures):
                    try:
                        response = future.result()
                        results["total_requests"] += 1

                        if response.status_code == 200:
                            results["successful_requests"] += 1
                        else:
                            results["failed_requests"] += 1

                        if hasattr(response, 'elapsed'):
                            results["response_times"].append(response.elapsed.total_seconds() * 1000)

                    except Exception as e:
                        results["total_requests"] += 1
                        results["failed_requests"] += 1

            results["end_time"] = time.time()
            duration = results["end_time"] - results["start_time"]

            if duration > 0:
                results["qps"] = results["total_requests"] / duration

            if results["total_requests"] > 0:
                results["error_rate"] = results["failed_requests"] / results["total_requests"]

            if results["response_times"]:
                results["avg_response_time_ms"] = statistics.mean(results["response_times"])
                results["p50_response_time_ms"] = percentile(results["response_times"], 50)
                results["p95_response_time_ms"] = percentile(results["response_times"], 95)
                results["p99_response_time_ms"] = percentile(results["response_times"], 99)

            allure.attach(
                f"总请求数: {results['total_requests']}\n"
                f"成功请求数: {results['successful_requests']}\n"
                f"失败请求数: {results['failed_requests']}\n"
                f"QPS: {results['qps']:.2f}\n"
                f"错误率: {results['error_rate']:.2%}\n"
                f"平均响应时间: {results.get('avg_response_time_ms', 0):.2f}ms\n"
                f"P50响应时间: {results.get('p50_response_time_ms', 0):.2f}ms\n"
                f"P95响应时间: {results.get('p95_response_time_ms', 0):.2f}ms\n"
                f"P99响应时间: {results.get('p99_response_time_ms', 0):.2f}ms",
                name=f"{test_name}吞吐量测试结果",
                attachment_type=allure.attachment_type.TEXT
            )

        return results
