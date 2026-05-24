"""
Mock服务器独立测试 - 验证mock服务是否正常工作
"""
import pytest
import requests
import time
import yaml
from mock.common_server import MockServerManager


@pytest.fixture(scope="module")
def mock_manager():
    """启动Mock服务器"""
    with open("config/mock_config.yaml") as f:
        config = yaml.safe_load(f)

    manager = MockServerManager(config)
    manager.start_all()
    time.sleep(1)  # 等待服务器启动

    yield manager

    manager.stop_all()


class TestOpenAIMock:
    """OpenAI Mock服务测试"""

    BASE_URL = "http://127.0.0.1:5001/v1"

    def test_chat_completion(self, mock_manager):
        """测试聊天补全接口"""
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "gpt-4"
        assert len(data["choices"]) > 0
        assert data["choices"][0]["message"]["content"] == "This is a mock response from OpenAI."

    def test_chat_completion_stream(self, mock_manager):
        """测试流式聊天补全"""
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            },
            stream=True
        )
        assert response.status_code == 200

        chunks = []
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: ') and line != 'data: [DONE]':
                    chunks.append(line)

        assert len(chunks) > 0

    def test_embeddings(self, mock_manager):
        """测试Embeddings接口"""
        response = requests.post(
            f"{self.BASE_URL}/embeddings",
            json={
                "model": "text-embedding-ada-002",
                "input": "Hello world"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0
        assert len(data["data"][0]["embedding"]) > 0

    def test_models(self, mock_manager):
        """测试模型列表接口"""
        response = requests.get(f"{self.BASE_URL}/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert len(data["data"]) > 0


class TestAnthropicMock:
    """Anthropic Mock服务测试"""

    BASE_URL = "http://127.0.0.1:5002/v1"

    def test_messages(self, mock_manager):
        """测试Messages接口"""
        response = requests.post(
            f"{self.BASE_URL}/messages",
            json={
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "message"
        assert data["model"] == "claude-sonnet-4-20250514"
        assert data["content"][0]["text"] == "This is a mock response from Anthropic."

    def test_messages_stream(self, mock_manager):
        """测试流式Messages接口"""
        response = requests.post(
            f"{self.BASE_URL}/messages",
            json={
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            },
            stream=True
        )
        assert response.status_code == 200

        chunks = []
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: ') and line != 'data: [DONE]':
                    chunks.append(line)

        assert len(chunks) > 0


class TestGoogleGeminiMock:
    """Google Gemini Mock服务测试"""

    BASE_URL = "http://127.0.0.1:5004/v1beta"

    def test_generate_content(self, mock_manager):
        """测试内容生成接口"""
        response = requests.post(
            f"{self.BASE_URL}/models/gemini-2.0-flash:generateContent",
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": "Hello"}
                        ]
                    }
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert len(data["candidates"]) > 0
        assert data["candidates"][0]["content"]["parts"][0]["text"] == "This is a mock response from Google Gemini."

    def test_generate_content_stream(self, mock_manager):
        """测试流式内容生成接口"""
        response = requests.post(
            f"{self.BASE_URL}/models/gemini-2.0-flash:streamGenerateContent",
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": "Hello"}
                        ]
                    }
                ]
            },
            stream=True
        )
        assert response.status_code == 200

        chunks = []
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    chunks.append(line)

        assert len(chunks) > 0

    def test_models(self, mock_manager):
        """测试模型列表接口"""
        response = requests.get(f"{self.BASE_URL}/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
