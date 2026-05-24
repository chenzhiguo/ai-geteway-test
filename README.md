# AI Gateway 自动化测试项目

## 项目简介

本项目是AI Gateway的自动化测试项目，用于测试类似于OpenRouter的大模型代理网关。项目覆盖了网关的所有接口类型，包括聊天补全、文本嵌入、图像生成、Responses接口和模型列表等。

## 项目特性

- **全面的接口测试**：覆盖所有LLM接口类型
- **性能测试**：吞吐量、延迟、并发测试
- **Mock服务器**：模拟OpenAI、Anthropic等LLM提供商
- **详细的测试报告**：支持终端、HTML和Allure报告
- **灵活的配置管理**：YAML配置文件，支持环境变量替换
- **完善的日志记录**：详细的请求/响应日志

## 项目结构

```
ai-gateway-test/
├── pyproject.toml              # Poetry配置文件
├── pytest.ini                  # pytest配置文件
├── conftest.py                 # pytest fixtures
├── README.md                   # 项目说明文档
├── config/                     # 配置文件目录
│   ├── test_config.yaml        # 测试配置
│   └── mock_config.yaml        # Mock服务器配置
├── e2e/                        # E2E测试目录
│   ├── __init__.py
│   ├── test_chat.py            # 聊天接口测试
│   ├── test_embedding.py       # 嵌入接口测试
│   ├── test_image.py           # 图像生成接口测试
│   ├── test_responses.py       # Responses接口测试
│   └── test_model_list.py      # 模型列表接口测试
├── performance/                # 性能测试目录
│   ├── __init__.py
│   ├── test_throughput.py      # 吞吐量测试
│   ├── test_latency.py         # 延迟测试
│   └── test_concurrency.py     # 并发测试
├── mock/                       # Mock服务器目录
│   ├── __init__.py
│   └── common_server.py        # 通用Mock服务器
├── utils/                      # 工具类目录
│   ├── __init__.py
│   ├── http_client.py          # HTTP客户端
│   ├── config_loader.py        # 配置加载器
│   └── logger.py               # 日志工具
├── reports/                    # 测试报告目录
└── docs/                       # 文档目录
```

## 环境要求

- Python 3.10+
- Poetry（依赖管理）

## 安装

### 1. 安装Poetry

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 或者使用pip安装
pip install poetry
```

### 2. 安装依赖

```bash
# 安装项目依赖
poetry install

# 或者使用pip安装
pip install -r requirements.txt
```

### 3. 配置环境

复制配置文件模板并修改：

```bash
cp config/test_config.yaml.example config/test_config.yaml
cp config/mock_config.yaml.example config/mock_config.yaml
```

编辑配置文件，设置网关地址、API密钥等参数。

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

#### 手动启动Mock服务器

```bash
# 启动OpenAI Mock服务器
python -m mock.common_server

# 或者使用Poetry运行
poetry run python -m mock.common_server
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

## 测试用例说明

### E2E测试

- **test_chat.py**：聊天补全接口测试
  - 正常流程
  - 流式响应
  - 边界条件
  - 错误处理
  - 网关特性

- **test_embedding.py**：文本嵌入接口测试
  - 正常流程
  - 批量嵌入
  - 边界条件
  - 错误处理
  - 网关特性

- **test_image.py**：图像生成接口测试
  - 正常流程
  - 不同尺寸
  - 多张图片
  - 边界条件
  - 错误处理
  - 网关特性

- **test_responses.py**：Responses接口测试
  - 正常流程
  - 流式响应
  - 多轮对话
  - 边界条件
  - 错误处理
  - 网关特性

- **test_model_list.py**：模型列表接口测试
  - 正常流程
  - 模型详情
  - 过滤功能
  - 边界条件
  - 错误处理
  - 网关特性

### 性能测试

- **test_throughput.py**：吞吐量测试
  - 聊天补全接口吞吐量
  - 文本嵌入接口吞吐量
  - 模型列表接口吞吐量

- **test_latency.py**：延迟测试
  - 聊天补全接口延迟
  - 文本嵌入接口延迟
  - 模型列表接口延迟
  - 流式响应延迟

- **test_concurrency.py**：并发测试
  - 聊天补全接口并发
  - 文本嵌入接口并发
  - 模型列表接口并发
  - 混合接口并发

## 开发指南

### 添加新的测试用例

1. 在相应的测试目录中创建新的测试文件
2. 使用`@pytest.mark`标记测试类型
3. 使用`@allure`装饰器添加Allure报告信息
4. 使用fixtures获取配置和客户端

### 添加新的Mock服务器

1. 在`mock/common_server.py`中创建新的Mock服务器类
2. 继承`MockServer`基类
3. 实现`_register_routes`方法
4. 在`MockServerManager`中注册新的服务器

### 修改配置

1. 编辑`config/test_config.yaml`修改测试配置
2. 编辑`config/mock_config.yaml`修改Mock服务器配置
3. 使用环境变量覆盖配置值

## 常见问题

### Q: 测试失败怎么办？

A: 检查以下几点：
1. 网关是否正常运行
2. 配置文件是否正确
3. API密钥是否有效
4. 网络连接是否正常

### Q: 如何查看详细日志？

A: 修改`config/test_config.yaml`中的日志级别：

```yaml
logging:
  level: "DEBUG"
```

### Q: 如何跳过性能测试？

A: 使用pytest标记跳过：

```bash
pytest -m "not performance"
```

### Q: 如何并行运行测试？

A: 使用pytest-xdist插件：

```bash
pytest -n auto
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者：Your Name
- 邮箱：your.email@example.com
- 项目地址：https://github.com/yourusername/ai-gateway-test