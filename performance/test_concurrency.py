"""
并发性能测试
"""
import pytest
import allure
import time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from performance.utils import percentile


@allure.epic("AI Gateway")
@allure.feature("性能测试")
@allure.story("并发测试")
class TestConcurrency:
    """并发测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, performance_config):
        """设置测试环境"""
        self.config = performance_config.get("concurrency", {})
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 50)

    @pytest.mark.performance
    def test_chat_completion_concurrency(self, http_client, e2e_config):
        """测试聊天补全接口并发性能"""
        model = e2e_config.get("models", {}).get("chat", ["gpt-4o"])[0]

        request_data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "stream": False
        }

        results = self._run_concurrency_test(
            http_client.chat_completion,
            request_data,
            "chat_completion"
        )

        assert results["success_rate"] >= 0.95
        assert results["avg_response_time_ms"] <= 1000

    @pytest.mark.performance
    def test_embedding_concurrency(self, http_client, e2e_config):
        """测试文本嵌入接口并发性能"""
        model = e2e_config.get("models", {}).get("embedding", ["text-embedding-ada-002"])[0]

        request_data = {
            "model": model,
            "input": "Hello world"
        }

        results = self._run_concurrency_test(
            http_client.embedding,
            request_data,
            "embedding"
        )

        assert results["success_rate"] >= 0.95
        assert results["avg_response_time_ms"] <= 500

    @pytest.mark.performance
    def test_model_list_concurrency(self, http_client):
        """测试模型列表接口并发性能"""
        results = self._run_concurrency_test(
            lambda: http_client.model_list(),
            None,
            "model_list"
        )

        assert results["success_rate"] >= 0.95
        assert results["avg_response_time_ms"] <= 200

    @pytest.mark.performance
    def test_image_generation_concurrency(self, http_client, e2e_config):
        """测试图片生成接口并发性能"""
        model = e2e_config.get("models", {}).get("image", ["dall-e-3"])[0]

        request_data = {
            "model": model,
            "prompt": "A sunset over a mountain landscape",
            "n": 1,
            "size": "256x256"
        }

        results = self._run_concurrency_test(
            http_client.image_generation,
            request_data,
            "image_generation"
        )

        assert results["success_rate"] >= 0.90
        assert results["avg_response_time_ms"] <= 5000

    @pytest.mark.performance
    def test_responses_concurrency(self, http_client, e2e_config):
        """测试Responses接口并发性能"""
        model = e2e_config.get("models", {}).get("responses", ["gpt-4"])[0]

        request_data = {
            "model": model,
            "input": "Hello, how are you?",
            "stream": False
        }

        results = self._run_concurrency_test(
            http_client.responses,
            request_data,
            "responses"
        )

        assert results["success_rate"] >= 0.95
        assert results["avg_response_time_ms"] <= 1000

    @pytest.mark.performance
    def test_messages_concurrency(self, http_client, e2e_config):
        """测试Messages接口并发性能"""
        model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]

        request_data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "max_tokens": 100
        }

        results = self._run_concurrency_test(
            http_client.messages,
            request_data,
            "messages"
        )

        assert results["success_rate"] >= 0.95
        assert results["avg_response_time_ms"] <= 1000

    @pytest.mark.performance
    def test_gemini_generate_concurrency(self, http_client, e2e_config):
        """测试Gemini生成接口并发性能"""
        model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        request_data = {
            "contents": [{"parts": [{"text": "Hello, how are you?"}]}]
        }

        results = self._run_concurrency_test(
            lambda data: http_client.gemini_generate(model, data),
            request_data,
            "gemini_generate"
        )

        assert results["success_rate"] >= 0.95
        assert results["avg_response_time_ms"] <= 1000

    @pytest.mark.performance
    def test_health_check_concurrency(self, http_client):
        """测试健康检查接口并发性能"""
        results = self._run_concurrency_test(
            lambda: http_client.health_check(),
            None,
            "health_check"
        )

        assert results["success_rate"] >= 0.99
        assert results["avg_response_time_ms"] <= 100

    @pytest.mark.performance
    def test_mixed_concurrency(self, http_client, e2e_config):
        """测试混合接口并发性能"""
        chat_model = e2e_config.get("models", {}).get("chat", ["gpt-4o"])[0]
        anthropic_model = e2e_config.get("models", {}).get("anthropic", ["claude-sonnet-4-20250514"])[0]
        gemini_model = e2e_config.get("models", {}).get("google", ["gemini-2.0-flash"])[0]

        requests = [
            (http_client.chat_completion, {
                "model": chat_model,
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }),
            (http_client.embedding, {
                "model": "text-embedding-ada-002",
                "input": "Hello world"
            }),
            (lambda: http_client.model_list(), None),
            (http_client.responses, {
                "model": chat_model,
                "input": "Hello",
                "stream": False
            }),
            (http_client.messages, {
                "model": anthropic_model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 50
            }),
            (lambda data: http_client.gemini_generate(gemini_model, data), {
                "contents": [{"parts": [{"text": "Hello"}]}]
            }),
            (lambda: http_client.health_check(), None),
        ]

        results = self._run_mixed_concurrency_test(requests, "mixed")

        assert results["success_rate"] >= 0.90

    def _run_concurrency_test(self, request_func, request_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """运行并发测试"""
        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "start_time": None,
            "end_time": None
        }

        with allure.step(f"运行{test_name}并发测试"):
            results["start_time"] = time.time()

            with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
                futures = []

                for i in range(self.max_concurrent_requests):
                    submit_time = time.time()
                    if request_data:
                        future = executor.submit(request_func, request_data)
                    else:
                        future = executor.submit(request_func)
                    futures.append((submit_time, future))

                for submit_time, future in futures:
                    try:
                        response = future.result()
                        response_time = (time.time() - submit_time) * 1000

                        results["response_times"].append(response_time)
                        results["total_requests"] += 1

                        if response.status_code == 200:
                            results["successful_requests"] += 1
                        else:
                            results["failed_requests"] += 1
                            results["errors"].append(f"HTTP {response.status_code}")

                    except Exception as e:
                        results["total_requests"] += 1
                        results["failed_requests"] += 1
                        results["errors"].append(str(e))

            results["end_time"] = time.time()

            if results["total_requests"] > 0:
                results["success_rate"] = results["successful_requests"] / results["total_requests"]
                results["error_rate"] = results["failed_requests"] / results["total_requests"]

            if results["response_times"]:
                results["avg_response_time_ms"] = sum(results["response_times"]) / len(results["response_times"])
                results["p50_response_time_ms"] = percentile(results["response_times"], 50)
                results["p95_response_time_ms"] = percentile(results["response_times"], 95)
                results["p99_response_time_ms"] = percentile(results["response_times"], 99)

            results["duration_seconds"] = results["end_time"] - results["start_time"]

            allure.attach(
                f"并发数: {self.max_concurrent_requests}\n"
                f"总请求数: {results['total_requests']}\n"
                f"成功请求数: {results['successful_requests']}\n"
                f"失败请求数: {results['failed_requests']}\n"
                f"成功率: {results.get('success_rate', 0):.2%}\n"
                f"错误率: {results.get('error_rate', 0):.2%}\n"
                f"平均响应时间: {results.get('avg_response_time_ms', 0):.2f}ms\n"
                f"P50响应时间: {results.get('p50_response_time_ms', 0):.2f}ms\n"
                f"P95响应时间: {results.get('p95_response_time_ms', 0):.2f}ms\n"
                f"P99响应时间: {results.get('p99_response_time_ms', 0):.2f}ms\n"
                f"总耗时: {results['duration_seconds']:.2f}s\n"
                f"错误详情: {results['errors'][:5] if results['errors'] else '无'}",
                name=f"{test_name}并发测试结果",
                attachment_type=allure.attachment_type.TEXT
            )

        return results

    def _run_mixed_concurrency_test(self, requests: List[tuple], test_name: str) -> Dict[str, Any]:
        """运行混合并发测试"""
        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "request_types": {},
            "start_time": None,
            "end_time": None
        }

        with allure.step(f"运行{test_name}混合并发测试"):
            results["start_time"] = time.time()

            with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
                futures = []

                for i in range(self.max_concurrent_requests):
                    request_func, request_data = requests[i % len(requests)]
                    submit_time = time.time()
                    if request_data:
                        future = executor.submit(request_func, request_data)
                    else:
                        future = executor.submit(request_func)
                    futures.append((submit_time, future, i % len(requests)))

                for submit_time, future, request_type in futures:
                    try:
                        response = future.result()
                        response_time = (time.time() - submit_time) * 1000

                        results["response_times"].append(response_time)
                        results["total_requests"] += 1

                        if request_type not in results["request_types"]:
                            results["request_types"][request_type] = {
                                "total": 0,
                                "successful": 0,
                                "failed": 0
                            }
                        results["request_types"][request_type]["total"] += 1

                        if response.status_code == 200:
                            results["successful_requests"] += 1
                            results["request_types"][request_type]["successful"] += 1
                        else:
                            results["failed_requests"] += 1
                            results["request_types"][request_type]["failed"] += 1
                            results["errors"].append(f"HTTP {response.status_code}")

                    except Exception as e:
                        results["total_requests"] += 1
                        results["failed_requests"] += 1
                        results["errors"].append(str(e))

            results["end_time"] = time.time()

            if results["total_requests"] > 0:
                results["success_rate"] = results["successful_requests"] / results["total_requests"]
                results["error_rate"] = results["failed_requests"] / results["total_requests"]

            if results["response_times"]:
                results["avg_response_time_ms"] = sum(results["response_times"]) / len(results["response_times"])

            results["duration_seconds"] = results["end_time"] - results["start_time"]

            allure.attach(
                f"并发数: {self.max_concurrent_requests}\n"
                f"总请求数: {results['total_requests']}\n"
                f"成功请求数: {results['successful_requests']}\n"
                f"失败请求数: {results['failed_requests']}\n"
                f"成功率: {results.get('success_rate', 0):.2%}\n"
                f"错误率: {results.get('error_rate', 0):.2%}\n"
                f"平均响应时间: {results.get('avg_response_time_ms', 0):.2f}ms\n"
                f"总耗时: {results['duration_seconds']:.2f}s\n"
                f"请求类型统计: {results['request_types']}\n"
                f"错误详情: {results['errors'][:5] if results['errors'] else '无'}",
                name=f"{test_name}混合并发测试结果",
                attachment_type=allure.attachment_type.TEXT
            )

        return results
