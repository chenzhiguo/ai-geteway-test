"""
通用Mock服务器管理器
"""
import json
import logging
import threading
import time
from typing import Dict, Any, List
from flask import Flask, request, jsonify
import yaml

logger = logging.getLogger(__name__)


class MockServer:
    """Mock服务器基类"""

    def __init__(self, name: str, host: str, port: int, base_path: str):
        self.name = name
        self.host = host
        self.port = port
        self.base_path = base_path
        self.app = Flask(__name__)
        self.server_thread = None
        self.is_running = False

        # 注册路由
        self._register_routes()

    def _register_routes(self):
        """注册路由（子类实现）"""
        pass

    def start(self):
        """启动服务器"""
        if self.is_running:
            logger.warning(f"Mock服务器 {self.name} 已经在运行")
            return

        self.server_thread = threading.Thread(
            target=self.app.run,
            kwargs={"host": self.host, "port": self.port, "debug": False, "use_reloader": False}
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        self.is_running = True
        logger.info(f"Mock服务器 {self.name} 已启动: http://{self.host}:{self.port}")

    def stop(self):
        """停止服务器"""
        # Flask没有直接的停止方法，需要通过线程结束
        self.is_running = False
        logger.info(f"Mock服务器 {self.name} 已停止")


class OpenAIMockServer(MockServer):
    """OpenAI Mock服务器"""

    def __init__(self, host: str, port: int, base_path: str):
        super().__init__("OpenAI", host, port, base_path)

    def _register_routes(self):
        """注册OpenAI API路由"""

        @self.app.route(f"{self.base_path}/chat/completions", methods=["POST"])
        def chat_completions():
            """聊天补全接口"""
            data = request.get_json()
            model = data.get("model", "gpt-4")
            messages = data.get("messages", [])
            stream = data.get("stream", False)

            if stream:
                return self._stream_chat_response(model, messages)
            else:
                return self._chat_response(model, messages)

        @self.app.route(f"{self.base_path}/embeddings", methods=["POST"])
        def embeddings():
            """文本嵌入接口"""
            data = request.get_json()
            model = data.get("model", "text-embedding-ada-002")
            input_text = data.get("input", "")

            return self._embedding_response(model, input_text)

        @self.app.route(f"{self.base_path}/images/generations", methods=["POST"])
        def image_generations():
            """图像生成接口"""
            data = request.get_json()
            model = data.get("model", "dall-e-3")
            prompt = data.get("prompt", "")
            n = data.get("n", 1)
            size = data.get("size", "1024x1024")

            return self._image_generation_response(model, prompt, n, size)

        @self.app.route(f"{self.base_path}/responses", methods=["POST"])
        def responses():
            """Responses接口"""
            data = request.get_json()
            model = data.get("model", "gpt-4")
            input_text = data.get("input", "")
            stream = data.get("stream", False)

            if stream:
                return self._stream_responses_response(model, input_text)
            else:
                return self._responses_response(model, input_text)

        @self.app.route(f"{self.base_path}/models", methods=["GET"])
        def models():
            """模型列表接口"""
            return self._model_list_response()

    def _chat_response(self, model: str, messages: List[Dict]) -> Dict:
        """生成聊天响应"""
        return jsonify({
            "id": "chatcmpl-mock-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from OpenAI."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        })

    def _stream_chat_response(self, model: str, messages: List[Dict]):
        """生成流式聊天响应"""
        def generate():
            chunks = [
                {"role": "assistant", "content": "This"},
                {"role": "assistant", "content": " is"},
                {"role": "assistant", "content": " a"},
                {"role": "assistant", "content": " mock"},
                {"role": "assistant", "content": " response."},
            ]

            for chunk in chunks:
                data = {
                    "id": "chatcmpl-mock-123",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": chunk,
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(data)}\n\n"

            # 结束标记
            yield "data: [DONE]\n\n"

        return self.app.response_class(
            generate(),
            mimetype='text/event-stream'
        )

    def _embedding_response(self, model: str, input_text: Any) -> Dict:
        """生成嵌入响应"""
        # 处理批量输入
        if isinstance(input_text, list):
            data = []
            for i, text in enumerate(input_text):
                data.append({
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": i
                })
        else:
            data = [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": 0
                }
            ]

        return jsonify({
            "object": "list",
            "data": data,
            "model": model,
            "usage": {
                "prompt_tokens": 5,
                "total_tokens": 5
            }
        })

    def _image_generation_response(self, model: str, prompt: str, n: int, size: str) -> Dict:
        """生成图像生成响应"""
        data = []
        for i in range(n):
            data.append({
                "url": f"https://example.com/image_{i}.png",
                "revised_prompt": prompt
            })

        return jsonify({
            "created": int(time.time()),
            "data": data
        })

    def _responses_response(self, model: str, input_text: Any) -> Dict:
        """生成Responses响应"""
        return jsonify({
            "id": "resp-mock-123",
            "object": "response",
            "created_at": int(time.time()),
            "model": model,
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "This is a mock response from Responses API."
                        }
                    ]
                }
            ],
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30
            }
        })

    def _stream_responses_response(self, model: str, input_text: Any):
        """生成流式Responses响应"""
        def generate():
            chunks = [
                {"type": "output_text", "text": "This"},
                {"type": "output_text", "text": " is"},
                {"type": "output_text", "text": " a"},
                {"type": "output_text", "text": " mock"},
                {"type": "output_text", "text": " response."},
            ]

            for chunk in chunks:
                data = {
                    "id": "resp-mock-123",
                    "object": "response.chunk",
                    "created_at": int(time.time()),
                    "model": model,
                    "output": [
                        {
                            "type": "message",
                            "role": "assistant",
                            "content": [chunk]
                        }
                    ]
                }
                yield f"data: {json.dumps(data)}\n\n"

            # 结束标记
            yield "data: [DONE]\n\n"

        return self.app.response_class(
            generate(),
            mimetype='text/event-stream'
        )

    def _model_list_response(self) -> Dict:
        """生成模型列表响应"""
        return jsonify({
            "object": "list",
            "data": [
                {
                    "id": "gpt-4",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openai"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openai"
                },
                {
                    "id": "text-embedding-ada-002",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openai"
                },
                {
                    "id": "dall-e-3",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openai"
                }
            ]
        })


class AnthropicMockServer(MockServer):
    """Anthropic Mock服务器"""

    def __init__(self, host: str, port: int, base_path: str):
        super().__init__("Anthropic", host, port, base_path)

    def _register_routes(self):
        """注册Anthropic API路由"""

        @self.app.route(f"{self.base_path}/messages", methods=["POST"])
        def messages():
            """消息接口"""
            data = request.get_json()
            model = data.get("model", "claude-sonnet-4-20250514")
            messages = data.get("messages", [])
            stream = data.get("stream", False)

            if stream:
                return self._stream_message_response(model, messages)
            else:
                return self._message_response(model, messages)

    def _message_response(self, model: str, messages: List[Dict]) -> Dict:
        """生成消息响应"""
        return jsonify({
            "id": "msg-mock-123",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "This is a mock response from Anthropic."
                }
            ],
            "model": model,
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20
            }
        })

    def _stream_message_response(self, model: str, messages: List[Dict]):
        """生成流式消息响应"""
        def generate():
            chunks = [
                {"type": "text", "text": "This"},
                {"type": "text", "text": " is"},
                {"type": "text", "text": " a"},
                {"type": "text", "text": " mock"},
                {"type": "text", "text": " response."},
            ]

            for chunk in chunks:
                data = {
                    "id": "msg-mock-123",
                    "type": "message",
                    "role": "assistant",
                    "content": [chunk],
                    "model": model
                }
                yield f"data: {json.dumps(data)}\n\n"

            # 结束标记
            yield "data: [DONE]\n\n"

        return self.app.response_class(
            generate(),
            mimetype='text/event-stream'
        )


class GoogleGeminiMockServer(MockServer):
    """Google Gemini Mock服务器"""

    def __init__(self, host: str, port: int, base_path: str):
        super().__init__("Google Gemini", host, port, base_path)

    def _register_routes(self):
        """注册Google Gemini API路由"""

        @self.app.route(f"{self.base_path}/models/<model>:generateContent", methods=["POST"])
        def generate_content(model):
            """内容生成接口"""
            data = request.get_json()
            return self._generate_response(model, data)

        @self.app.route(f"{self.base_path}/models/<model>:streamGenerateContent", methods=["POST"])
        def stream_generate_content(model):
            """流式内容生成接口"""
            data = request.get_json()
            return self._stream_generate_response(model, data)

        @self.app.route(f"{self.base_path}/models", methods=["GET"])
        def list_models():
            """模型列表接口"""
            return self._model_list_response()

    def _generate_response(self, model: str, data: Dict) -> Dict:
        """生成响应"""
        return jsonify({
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "This is a mock response from Google Gemini."
                            }
                        ],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 20,
                "totalTokenCount": 30
            },
            "modelVersion": model
        })

    def _stream_generate_response(self, model: str, data: Dict):
        """生成流式响应"""
        def generate():
            chunks = [
                "This",
                " is",
                " a",
                " mock",
                " response.",
            ]

            for text in chunks:
                chunk_data = {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": text
                                    }
                                ],
                                "role": "model"
                            },
                            "index": 0
                        }
                    ]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

            # 最终chunk包含usageMetadata
            final_chunk = {
                "candidates": [
                    {
                        "content": {
                            "parts": [],
                            "role": "model"
                        },
                        "finishReason": "STOP",
                        "index": 0
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 10,
                    "candidatesTokenCount": 20,
                    "totalTokenCount": 30
                }
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"

        return self.app.response_class(
            generate(),
            mimetype='text/event-stream'
        )

    def _model_list_response(self) -> Dict:
        """生成模型列表响应"""
        return jsonify({
            "models": [
                {
                    "name": "models/gemini-2.0-flash",
                    "displayName": "Gemini 2.0 Flash",
                    "description": "Fast and versatile performance",
                    "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]
                },
                {
                    "name": "models/gemini-pro",
                    "displayName": "Gemini Pro",
                    "description": "Best for scaling across tasks",
                    "supportedGenerationMethods": ["generateContent", "streamGenerateContent"]
                }
            ]
        })


class MockServerManager:
    """Mock服务器管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.servers: Dict[str, MockServer] = {}

    def start_all(self):
        """启动所有Mock服务器"""
        mock_servers_config = self.config.get("mock_servers", {})

        # 启动OpenAI Mock服务器
        if "openai" in mock_servers_config:
            openai_config = mock_servers_config["openai"]
            server = OpenAIMockServer(
                host=openai_config.get("host", "127.0.0.1"),
                port=openai_config.get("port", 5001),
                base_path=openai_config.get("base_path", "/v1")
            )
            server.start()
            self.servers["openai"] = server

        # 启动Anthropic Mock服务器
        if "anthropic" in mock_servers_config:
            anthropic_config = mock_servers_config["anthropic"]
            server = AnthropicMockServer(
                host=anthropic_config.get("host", "127.0.0.1"),
                port=anthropic_config.get("port", 5002),
                base_path=anthropic_config.get("base_path", "/v1")
            )
            server.start()
            self.servers["anthropic"] = server

        # 启动Google Gemini Mock服务器
        if "google" in mock_servers_config:
            google_config = mock_servers_config["google"]
            server = GoogleGeminiMockServer(
                host=google_config.get("host", "127.0.0.1"),
                port=google_config.get("port", 5004),
                base_path=google_config.get("base_path", "/v1beta")
            )
            server.start()
            self.servers["google"] = server

        # 等待服务器启动
        time.sleep(1)

    def stop_all(self):
        """停止所有Mock服务器"""
        for server in self.servers.values():
            server.stop()
        self.servers.clear()

    def get_server(self, name: str) -> MockServer:
        """获取指定的Mock服务器"""
        return self.servers.get(name)

    def is_running(self, name: str) -> bool:
        """检查指定的Mock服务器是否在运行"""
        server = self.servers.get(name)
        return server.is_running if server else False