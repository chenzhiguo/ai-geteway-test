# AI Gateway 自动化测试项目

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-7.4+-green.svg)](https://docs.pytest.org/)
[![Test](https://github.com/chenzhiguo/ai-gateway-test/actions/workflows/test.yml/badge.svg)](https://github.com/chenzhiguo/ai-gateway-test/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

本项目是AI Gateway的自动化测试项目，用于测试类似于OpenRouter的大模型代理网关。项目覆盖了网关的所有接口类型，包括聊天补全、文本嵌入、图像生成、Responses接口和模型列表等。

**GitHub仓库**: [ai-gateway-test](https://github.com/chenzhiguo/ai-gateway-test)

## 项目特性

### 测试覆盖

- **E2E测试**：覆盖主流LLM提供商接口
  - OpenAI接口（Chat、Embedding、Image、Responses、Models）
  - Anthropic接口（Messages）
  - Google接口（Gemini Generate Content）

- **性能测试**：全面的性能指标监控
  - 吞吐量测试（QPS）
  - 延迟测试（P50、P95、P99）
  - 并发测试

### 测试特性

- **Mock服务器**：模拟OpenAI、Anthropic、Google Gemini等LLM提供商
- **测试报告**：支持终端、HTML和Allure报告
- **配置管理**：YAML配置文件，支持环境变量替换
- **日志记录**：详细的请求/响应日志
- **CI/CD集成**：GitHub Actions自动测试

### 测试场景

- 正常流程测试
- 边界条件测试
- 错误处理测试
- 网关特性测试（Failover、熔断、限流等）
- 流式响应测试
- 批量请求测试

## 项目结构

```
ai-gateway-test/
├── .github/                    # GitHub配置
│   └── workflows/              # GitHub Actions工作流
├── config/                     # 配置文件目录
│   ├── test_config.yaml        # 测试配置
│   └── mock_config.yaml        # Mock服务器配置
├── docs/                       # 文档目录
│   ├── adr/                    # 架构决策记录
│   └── agents/                 # Agent技能配置
├── e2e/                        # E2E测试目录
│   ├── test_openai.py          # OpenAI接口测试
│   ├── test_anthropic.py       # Anthropic接口测试
│   ├── test_google.py          # Google Gemini接口测试
│   ├── test_embedding.py       # 嵌入接口测试
│   ├── test_image.py           # 图像生成接口测试
│   ├── test_responses.py       # Responses接口测试
│   └── test_model_list.py      # 模型列表接口测试
├── mock/                       # Mock服务器目录
│   └── common_server.py        # 通用Mock服务器
├── performance/                # 性能测试目录
│   ├── test_throughput.py      # 吞吐量测试
│   ├── test_latency.py         # 延迟测试
│   └── test_concurrency.py     # 并发测试
├── utils/                      # 工具类目录
│   ├── http_client.py          # HTTP客户端
│   ├── config_loader.py        # 配置加载器
│   └── logger.py               # 日志工具
├── CHANGELOG.md                # 更新日志
├── CLAUDE.md                   # Claude Code配置
├── CONTRIBUTING.md             # 贡献指南
├── CONTEXT.md                  # 术语表
├── LICENSE                     # MIT许可证
├── Makefile                    # 构建命令
├── README.md                   # 项目说明文档
├── conftest.py                 # pytest fixtures
├── pyproject.toml              # Poetry配置文件
├── pytest.ini                  # pytest配置文件
└── requirements.txt            # Python依赖
```

## 快速开始

### 环境要求

- Python 3.10+
- Poetry（推荐）或 pip

### 安装

#### 方式一：使用Poetry（推荐）

```bash
# 克隆项目
git clone https://github.com/chenzhiguo/ai-gateway-test.git
cd ai-gateway-test

# 安装Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

#### 方式二：使用pip

```bash
# 克隆项目
git clone https://github.com/chenzhiguo/ai-gateway-test.git
cd ai-gateway-test

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

编辑配置文件，设置网关地址、API密钥等参数：

```bash
# 编辑测试配置
vim config/test_config.yaml

# 编辑Mock服务器配置
vim config/mock_config.yaml
```

### 运行测试

```bash
# 运行所有测试
./venv/bin/pytest

# 迋试远程Gateway
GATEWAY_URL="http://your-gateway:port" ./venv/bin/pytest e2e/ -v

# 使用Makefile测试远程Gateway
make test-gw GATEWAY_URL="http://your-gateway:port"

# 运行E2E测试
./venv/bin/pytest e2e/

# 运行Mock服务器测试
make test-mock

# 运行性能测试
./venv/bin/pytest performance/

# 运行冒烟测试
./venv/bin/pytest -m smoke

# 生成HTML报告
./venv/bin/pytest --html=reports/report.html --self-contained-html

# 生成Allure报告
./venv/bin/pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report
```

## 使用方法

### 运行测试

#### 运行所有测试

```bash
# 使用Poetry运行
poetry run pytest

# 或者直接运行
pytest
```

#### 运行E2E测试

```bash
pytest e2e/
```

#### 运行性能测试

```bash
pytest performance/
```

#### 运行特定测试

```bash
# 运行聊天接口测试
pytest e2e/test_chat.py

# 运行吞吐量测试
pytest performance/test_throughput.py

# 运行冒烟测试
pytest -m smoke
```

### 测试报告

#### 生成HTML报告

```bash
pytest --html=reports/report.html --self-contained-html
```

#### 生成Allure报告

```bash
# 运行测试并生成Allure数据
pytest --alluredir=reports/allure-results

# 生成Allure报告
allure generate reports/allure-results -o reports/allure-report

# 打开Allure报告
allure open reports/allure-report
```

#### 查看终端报告

pytest会自动在终端显示测试结果。

### Mock服务器

测试项目会自动启动Mock服务器来模拟LLM提供商。Mock服务器配置在`config/mock_config.yaml`中。

支持的Mock服务：
- **OpenAI** (端口5001)：Chat、Embedding、Image、Responses、Models
- **Anthropic** (端口5002)：Messages
- **Google Gemini** (端口5004)：Generate Content
- **DeepSeek** (端口5003)：配置已添加，复用OpenAI格式

#### 运行Mock服务器测试

```bash
# 测试Mock服务器是否正常工作
make test-mock

# 或者直接运行
./venv/bin/pytest tests/test_mock_server.py -v
```

## 配置说明

### 测试配置

测试配置文件`config/test_config.yaml`包含以下配置：

- **gateway**：网关配置（URL、API密钥、超时时间）
- **e2e**：E2E测试配置（模型、场景、超时）
- **performance**：性能测试配置（QPS、延迟、并发）
- **test_data**：测试数据配置
- **logging**：日志配置
- **reporting**：报告配置

### Mock服务器配置

Mock服务器配置文件`config/mock_config.yaml`包含以下配置：

- **mock_servers**：Mock服务器配置（OpenAI、Anthropic等）
- **response_templates**：响应模板
- **error_responses**：错误响应模板

## 测试用例统计

| 测试类型 | 测试文件 | 测试用例数 | 测试场景 |
|---------|---------|-----------|---------|
| E2E测试 | test_openai.py | 5 | OpenAI聊天补全接口 |
| E2E测试 | test_anthropic.py | 5 | Anthropic Messages接口 |
| E2E测试 | test_google.py | 6 | Google Gemini接口 |
| E2E测试 | test_embedding.py | 5 | 文本嵌入接口 |
| E2E测试 | test_image.py | 6 | 图像生成接口 |
| E2E测试 | test_responses.py | 6 | Responses接口 |
| E2E测试 | test_model_list.py | 5 | 模型列表接口 |
| Mock测试 | test_mock_server.py | 9 | Mock服务器验证 |
| 性能测试 | test_throughput.py | 3 | 吞吐量测试 |
| 性能测试 | test_latency.py | 4 | 延迟测试 |
| 性能测试 | test_concurrency.py | 4 | 并发测试 |
| **总计** | **11个文件** | **58个用例** | - |

## 测试用例说明

### E2E测试

#### OpenAI聊天补全接口（test_openai.py）
- **正常流程**：测试基本聊天功能
- **流式响应**：测试SSE流式响应
- **边界条件**：测试空消息、超长消息等
- **错误处理**：测试无效模型、无效请求体等
- **网关特性**：测试多消息、温度参数、最大令牌数等

#### Anthropic Messages接口（test_anthropic.py）
- **正常流程**：测试基本消息功能
- **流式响应**：测试SSE流式响应
- **多轮对话**：测试多轮对话
- **系统提示**：测试系统提示词
- **错误处理**：测试无效模型、无效请求体等

#### Google Gemini接口（test_google.py）
- **正常流程**：测试基本内容生成功能
- **流式响应**：测试SSE流式响应
- **多轮对话**：测试多轮对话
- **系统指令**：测试系统指令
- **生成参数**：测试温度、最大输出令牌数等参数
- **错误处理**：测试无效模型、无效请求体等

#### 文本嵌入接口（test_embedding.py）
- **正常流程**：测试基本嵌入功能
- **批量嵌入**：测试批量文本嵌入
- **边界条件**：测试空输入、超长文本等
- **错误处理**：测试无效模型、无效请求体等
- **网关特性**：测试不同维度、编码格式等

#### 图像生成接口（test_image.py）
- **正常流程**：测试基本图像生成功能
- **不同尺寸**：测试不同图像尺寸
- **多张图片**：测试生成多张图片
- **边界条件**：测试空提示、超长提示等
- **错误处理**：测试无效模型、无效尺寸等
- **网关特性**：测试不同质量、风格等

#### Responses接口（test_responses.py）
- **正常流程**：测试基本Responses功能
- **流式响应**：测试SSE流式响应
- **多轮对话**：测试多轮对话
- **边界条件**：测试空输入、超长输入等
- **错误处理**：测试无效模型、无效请求体等
- **网关特性**：测试温度参数、最大输出令牌数、工具调用等

#### 模型列表接口（test_model_list.py）
- **正常流程**：测试获取模型列表
- **模型详情**：测试模型详细信息
- **过滤功能**：测试按提供商过滤
- **边界条件**：测试分页参数等
- **错误处理**：测试无效参数等
- **网关特性**：测试模型类型、ID格式等

### 性能测试

#### 吞吐量测试（test_throughput.py）
- **聊天补全接口吞吐量**：测试QPS
- **文本嵌入接口吞吐量**：测试QPS
- **模型列表接口吞吐量**：测试QPS

#### 延迟测试（test_latency.py）
- **聊天补全接口延迟**：测试P50、P95、P99
- **文本嵌入接口延迟**：测试P50、P95、P99
- **模型列表接口延迟**：测试P50、P95、P99
- **流式响应延迟**：测试首字节时间（TTFT）

#### 并发测试（test_concurrency.py）
- **聊天补全接口并发**：测试并发性能
- **文本嵌入接口并发**：测试并发性能
- **模型列表接口并发**：测试并发性能
- **混合接口并发**：测试混合接口并发性能

## 常用命令

### Makefile命令

```bash
# 查看所有可用命令
make help

# 安装依赖
make install

# 运行所有测试
make test

# 运行E2E测试
make test-e2e

# 运行Mock服务器测试
make test-mock

# 测试远程Gateway
make test-gw GATEWAY_URL=http://your-gateway:port

# 运行性能测试
make test-performance

# 运行冒烟测试
make test-smoke

# 运行回归测试
make test-regression

# 生成测试报告
make report

# 打开测试报告
make open-report

# 清理临时文件
make clean

# 代码检查
make lint

# 格式化代码
make format

# 类型检查
make type-check

# 运行所有检查
make check
```

### pytest命令

```bash
# 运行所有测试
./venv/bin/pytest

# 运行E2E测试
./venv/bin/pytest e2e/

# 运行Mock服务器测试
./venv/bin/pytest tests/test_mock_server.py

# 运行性能测试
./venv/bin/pytest performance/

# 运行特定测试文件
./venv/bin/pytest e2e/test_openai.py

# 运行特定测试用例
./venv/bin/pytest e2e/test_openai.py::TestChatCompletion::test_chat_completion_normal

# 运行冒烟测试
./venv/bin/pytest -m smoke

# 运行回归测试
./venv/bin/pytest -m regression

# 跳过性能测试
./venv/bin/pytest -m "not performance"

# 并行运行测试
./venv/bin/pytest -n auto

# 生成HTML报告
./venv/bin/pytest --html=reports/report.html --self-contained-html

# 生成Allure报告
./venv/bin/pytest --alluredir=reports/allure-results

# 查看详细日志
./venv/bin/pytest -v --log-cli-level=DEBUG

# 失败后重新运行
./venv/bin/pytest --reruns=3

# 设置超时时间
./venv/bin/pytest --timeout=60
```

## 开发指南

### 添加新的测试用例

1. 在相应的测试目录中创建新的测试文件
2. 使用`@pytest.mark`标记测试类型
3. 使用`@allure`装饰器添加Allure报告信息
4. 使用fixtures获取配置和客户端

示例：
```python
import pytest
import allure

@allure.epic("AI Gateway")
@allure.feature("新接口")
@allure.story("正常流程")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.smoke
def test_new_feature(self, http_client, e2e_config):
    """测试新功能"""
    # 测试代码
```

### 添加新的Mock服务器

1. 在`mock/common_server.py`中创建新的Mock服务器类
2. 继承`MockServer`基类
3. 实现`_register_routes`方法
4. 在`MockServerManager`中注册新的服务器

示例：
```python
class NewProviderMockServer(MockServer):
    """新提供商Mock服务器"""

    def __init__(self, host: str, port: int, base_path: str):
        super().__init__("NewProvider", host, port, base_path)

    def _register_routes(self):
        """注册路由"""
        @self.app.route(f"{self.base_path}/endpoint", methods=["POST"])
        def endpoint():
            # 处理逻辑
            return jsonify({"response": "mock response"})
```

### 修改配置

1. 编辑`config/test_config.yaml`修改测试配置
2. 编辑`config/mock_config.yaml`修改Mock服务器配置
3. 使用环境变量覆盖配置值

环境变量示例：
```bash
export GATEWAY_URL="http://your-gateway:port"
export GATEWAY_API_KEY="your-api-key"

# 或者一行运行测试
GATEWAY_URL="http://your-gateway:port" ./venv/bin/pytest e2e/
```

## 性能基准

### 测试环境

- **CPU**: 4核
- **内存**: 8GB
- **网络**: 本地网络
- **Python**: 3.10+

### 性能目标

| 接口类型 | QPS目标 | P50延迟 | P95延迟 | P99延迟 |
|---------|---------|---------|---------|---------|
| 聊天补全 | 100 | <200ms | <500ms | <1000ms |
| 文本嵌入 | 200 | <100ms | <200ms | <500ms |
| 模型列表 | 500 | <50ms | <100ms | <200ms |

### 运行性能测试

```bash
# 运行所有性能测试
pytest performance/

# 运行吞吐量测试
pytest performance/test_throughput.py

# 运行延迟测试
pytest performance/test_latency.py

# 运行并发测试
pytest performance/test_concurrency.py

# 生成性能报告
pytest performance/ --html=reports/performance-report.html
```

### 性能测试配置

编辑`config/test_config.yaml`中的性能测试配置：

```yaml
performance:
  # 吞吐量测试
  throughput:
    target_qps: 100
    duration_seconds: 60
    ramp_up_seconds: 10

  # 延迟测试
  latency:
    target_p50_ms: 200
    target_p95_ms: 500
    target_p99_ms: 1000

  # 并发测试
  concurrency:
    max_concurrent_requests: 50
    connection_pool_size: 100
```

## 常见问题

### Q: 测试失败怎么办？

A: 检查以下几点：
1. 网关是否正常运行
2. 配置文件是否正确
3. API密钥是否有效
4. 网络连接是否正常
5. 查看详细日志：`./venv/bin/pytest -v --log-cli-level=DEBUG`

### Q: 如何测试远程Gateway？

A: 使用环境变量指定Gateway地址：
```bash
# 方式1：设置环境变量
export GATEWAY_URL="http://your-gateway:port"
export GATEWAY_API_KEY="your-api-key"
./venv/bin/pytest e2e/

# 方式2：一行命令
GATEWAY_URL="http://your-gateway:port" ./venv/bin/pytest e2e/ -v

# 方式3：使用Makefile
make test-gw GATEWAY_URL="http://your-gateway:port"
```

### Q: 如何查看详细日志？

A: 有几种方式：
```bash
# 方式1：命令行参数
pytest -v --log-cli-level=DEBUG

# 方式2：修改配置文件
# 编辑 config/test_config.yaml
logging:
  level: "DEBUG"

# 方式3：查看日志文件
cat logs/test.log
```

### Q: 如何跳过性能测试？

A: 使用pytest标记跳过：
```bash
# 跳过性能测试
pytest -m "not performance"

# 只运行E2E测试
pytest e2e/

# 只运行冒烟测试
pytest -m smoke
```

### Q: 如何并行运行测试？

A: 使用pytest-xdist插件：
```bash
# 自动检测CPU核心数
pytest -n auto

# 指定进程数
pytest -n 4

# 安装pytest-xdist（如果未安装）
pip install pytest-xdist
```

### Q: 如何生成测试报告？

A: 支持多种报告格式：
```bash
# HTML报告
pytest --html=reports/report.html --self-contained-html

# Allure报告
pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report
allure open reports/allure-report

# 终端报告（默认）
pytest -v
```

### Q: 如何Mock外部依赖？

A: 使用项目的Mock服务器：
```bash
# 启动Mock服务器
make mock

# 或者手动启动
python -m mock.common_server
```

### Q: 如何添加新的测试接口？

A: 参考以下步骤：
1. 在`e2e/`目录创建新的测试文件
2. 参考现有测试文件的结构
3. 使用fixtures获取配置和客户端
4. 添加适当的pytest标记和Allure装饰器

### Q: 如何配置不同的测试环境？

A: 使用环境变量或配置文件：
```bash
# 使用环境变量
export TEST_GATEWAY_URL="http://staging.example.com:8080"
export TEST_GATEWAY_API_KEY="staging-api-key"

# 或者创建不同的配置文件
cp config/test_config.yaml config/test_config.staging.yaml
# 编辑配置文件
# 运行测试时指定配置
TEST_CONFIG_PATH=config/test_config.staging.yaml pytest
```

### Q: 如何调试测试失败？

A: 使用以下方法：
```bash
# 1. 查看详细输出
pytest -v -s

# 2. 只运行失败的测试
pytest --lf

# 3. 失败后进入调试器
pytest --pdb

# 4. 查看测试覆盖率
pytest --cov=e2e --cov-report=html
```

### Q: 如何贡献代码？

A: 参考[CONTRIBUTING.md](CONTRIBUTING.md)文件：
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## CI/CD

项目使用GitHub Actions进行持续集成。每次推送到`main`分支或创建Pull Request时，会自动运行测试。

### GitHub Actions工作流

- **测试**: 运行所有测试用例
- **代码检查**: 运行lint和类型检查
- **报告生成**: 生成测试覆盖率报告

### 本地运行CI检查

```bash
# 运行所有检查
make check

# 运行代码检查
make lint

# 运行类型检查
make type-check
```

## 项目路线图

### 已完成

- [x] 项目初始化
- [x] E2E测试框架
- [x] 性能测试框架
- [x] Mock服务器（OpenAI、Anthropic、Google Gemini）
- [x] 配置管理
- [x] 日志记录
- [x] CI/CD集成
- [x] 测试报告
- [x] Anthropic Messages接口支持
- [x] Google Gemini接口支持
- [x] 环境变量配置覆盖

### 计划中

- [ ] 添加DeepSeek等更多LLM提供商支持
- [ ] 添加压力测试
- [ ] 添加稳定性测试
- [ ] 添加混沌测试
- [ ] 添加可视化测试报告
- [ ] 添加测试覆盖率报告
- [ ] 添加性能趋势分析
- [ ] 添加自动化测试数据生成
- [ ] 添加测试环境管理
- [ ] 添加分布式测试支持

### 长期目标

- [ ] 支持多种测试框架
- [ ] 支持多种报告格式
- [ ] 支持多种部署方式
- [ ] 支持多种监控系统集成
- [ ] 支持多种告警方式

## 贡献指南

我们欢迎任何形式的贡献！请阅读[CONTRIBUTING.md](CONTRIBUTING.md)了解详细信息。

### 快速贡献

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 提交规范

请遵循[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

类型（type）：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD相关

示例：
```
feat(e2e): add new test case for chat completion
fix(mock): fix mock server response format
docs(readme): update installation guide
test(performance): add latency test for embedding
```

## 联系方式

- **项目维护者**: chenzhiguo
- **GitHub**: [@chenzhiguo](https://github.com/chenzhiguo)
- **项目地址**: [ai-gateway-test](https://github.com/chenzhiguo/ai-gateway-test)
- **问题反馈**: [GitHub Issues](https://github.com/chenzhiguo/ai-gateway-test/issues)
- **功能建议**: [GitHub Discussions](https://github.com/chenzhiguo/ai-gateway-test/discussions)

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
