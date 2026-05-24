"""
延迟性能测试
"""
import pytest
import allure
import time
import statistics
from typing import Dict, Any
from performance.utils import percentile


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
        model = e2e_config.get("models", {}).get("chat", ["gpt-4o"])[0]

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

        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_image_generation_latency(self, http_client, e2e_config):
        """测试图片生成接口延迟"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]

        request_data = {
            "model": model,
            "prompt": "A sunset over a mountain landscape",
            "n": 1,
            "size": "256x256"
        }

        image_p50 = self.config.get("image_target_p50_ms", 3000)
        image_p95 = self.config.get("image_target_p95_ms", 5000)
        image_p99 = self.config.get("image_target_p99_ms", 8000)

        results = self._run_latency_test(
            http_client.image_generation,
            request_data,
            "image_generation"
        )

        assert results["p50_ms"] <= image_p50
        assert results["p95_ms"] <= image_p95
        assert results["p99_ms"] <= image_p99

    @pytest.mark.performance
    def test_responses_latency(self, http_client, e2e_config):
        """测试Responses接口延迟"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "input": "Hello, how are you?",
            "stream": False
        }

        results = self._run_latency_test(
            http_client.responses,
            request_data,
            "responses"
        )

        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_messages_latency(self, http_client, e2e_config):
        """测试Messages接口延迟"""
        model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]

        request_data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "max_tokens": 100
        }

        results = self._run_latency_test(
            http_client.messages,
            request_data,
            "messages"
        )

        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_gemini_generate_latency(self, http_client, e2e_config):
        """测试Gemini生成接口延迟"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "contents": [{"parts": [{"text": "Hello, how are you?"}]}]
        }

        results = self._run_latency_test(
            lambda data: http_client.gemini_generate(model, data),
            request_data,
            "gemini_generate"
        )

        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms
        assert results["p99_ms"] <= self.target_p99_ms

    @pytest.mark.performance
    def test_health_check_latency(self, http_client):
        """测试健康检查接口延迟"""
        health_p50 = self.config.get("health_target_p50_ms", 50)
        health_p95 = self.config.get("health_target_p95_ms", 100)
        health_p99 = self.config.get("health_target_p99_ms", 200)

        results = self._run_latency_test(
            lambda: http_client.health_check(),
            None,
            "health_check"
        )

        assert results["p50_ms"] <= health_p50
        assert results["p95_ms"] <= health_p95
        assert results["p99_ms"] <= health_p99

    @pytest.mark.performance
    def test_stream_latency(self, http_client, e2e_config):
        """测试流式响应延迟"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4o"])[0]

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

        assert results["ttft_ms"] <= self.target_p50_ms
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms

    @pytest.mark.performance
    def test_responses_stream_latency(self, http_client, e2e_config):
        """测试Responses流式响应延迟"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "input": "Tell me a short story",
            "stream": True
        }

        results = self._run_stream_latency_test(
            http_client.responses_stream,
            request_data,
            "stream_responses"
        )

        assert results["ttft_ms"] <= self.target_p50_ms
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms

    @pytest.mark.performance
    def test_messages_stream_latency(self, http_client, e2e_config):
        """测试Messages流式响应延迟"""
        model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]

        request_data = {
            "model": model,
            "messages": [{"role": "user", "content": "Tell me a short story"}],
            "max_tokens": 100,
            "stream": True
        }

        results = self._run_stream_latency_test(
            http_client.messages_stream,
            request_data,
            "stream_messages"
        )

        assert results["ttft_ms"] <= self.target_p50_ms
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms

    @pytest.mark.performance
    def test_gemini_stream_latency(self, http_client, e2e_config):
        """测试Gemini流式响应延迟"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "contents": [{"parts": [{"text": "Tell me a short story"}]}]
        }

        results = self._run_stream_latency_test(
            lambda data: http_client.gemini_stream(model, data),
            request_data,
            "stream_gemini"
        )

        assert results["ttft_ms"] <= self.target_p50_ms
        assert results["p50_ms"] <= self.target_p50_ms
        assert results["p95_ms"] <= self.target_p95_ms

    def _run_latency_test(self, request_func, request_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """运行延迟测试"""
        results = {
            "response_times": [],
            "successful_requests": 0,
            "failed_requests": 0,
            "total_requests": 100
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
                    response_time = (end_time - start_time) * 1000

                    results["response_times"].append(response_time)

                    if response.status_code == 200:
                        results["successful_requests"] += 1
                    else:
                        results["failed_requests"] += 1

                except Exception as e:
                    results["failed_requests"] += 1

            if results["response_times"]:
                results["avg_ms"] = statistics.mean(results["response_times"])
                results["p50_ms"] = statistics.median(results["response_times"])
                results["p95_ms"] = percentile(results["response_times"], 95)
                results["p99_ms"] = percentile(results["response_times"], 99)
                results["min_ms"] = min(results["response_times"])
                results["max_ms"] = max(results["response_times"])
                results["std_dev_ms"] = statistics.stdev(results["response_times"]) if len(results["response_times"]) > 1 else 0
            else:
                results["avg_ms"] = 0
                results["p50_ms"] = 0
                results["p95_ms"] = 0
                results["p99_ms"] = 0
                results["min_ms"] = 0
                results["max_ms"] = 0
                results["std_dev_ms"] = 0

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
            "ttft_times": [],
            "total_times": [],
            "successful_requests": 0,
            "failed_requests": 0,
            "total_requests": 50
        }

        with allure.step(f"运行{test_name}流式延迟测试"):
            for i in range(results["total_requests"]):
                try:
                    start_time = time.time()

                    response = request_func(request_data)

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

            if results["ttft_times"]:
                results["ttft_ms"] = statistics.mean(results["ttft_times"])
                results["ttft_p50_ms"] = statistics.median(results["ttft_times"])
                results["ttft_p95_ms"] = percentile(results["ttft_times"], 95)
            else:
                results["ttft_ms"] = 0
                results["ttft_p50_ms"] = 0
                results["ttft_p95_ms"] = 0

            if results["total_times"]:
                results["avg_ms"] = statistics.mean(results["total_times"])
                results["p50_ms"] = statistics.median(results["total_times"])
                results["p95_ms"] = percentile(results["total_times"], 95)
                results["p99_ms"] = percentile(results["total_times"], 99)
            else:
                results["avg_ms"] = 0
                results["p50_ms"] = 0
                results["p95_ms"] = 0
                results["p99_ms"] = 0

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
