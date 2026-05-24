# 贡献指南

感谢您对AI Gateway测试项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请通过[GitHub Issues](https://github.com/chenzhiguo/ai-gateway-test/issues)提交。

请包含以下信息：
- 问题的详细描述
- 复现步骤
- 预期行为和实际行为
- 环境信息（Python版本、操作系统等）

### 提交代码

1. **Fork项目**
   - 点击项目右上角的"Fork"按钮

2. **克隆您的Fork**
   ```bash
   git clone https://github.com/yourusername/ai-gateway-test.git
   cd ai-gateway-test
   ```

3. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **安装依赖**
   ```bash
   # 使用Poetry
   poetry install

   # 或使用pip
   pip install -r requirements.txt
   ```

5. **进行更改**
   - 编写代码
   - 添加测试
   - 更新文档

6. **运行测试**
   ```bash
   # 运行所有测试
   pytest

   # 运行特定测试
   pytest e2e/test_chat.py

   # 运行代码检查
   make check
   ```

7. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

8. **推送到您的Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **创建Pull Request**
   - 访问您的Fork页面
   - 点击"New Pull Request"
   - 填写PR描述

## 开发规范

### 代码风格

- 使用Python 3.10+语法
- 遵循PEP 8代码规范
- 使用类型注解
- 保持代码简洁

### 提交规范

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

类型（type）：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响代码运行的变更）
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

### 测试规范

- 每个测试用例应该独立且可重复
- 使用描述性的测试名称
- 使用fixtures管理测试数据
- 使用markers标记测试类型
- 添加Allure报告装饰器

示例：
```python
@allure.epic("AI Gateway")
@allure.feature("聊天补全接口")
@allure.story("正常流程")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.smoke
def test_chat_completion_normal(self, http_client, e2e_config):
    """测试聊天补全接口正常流程"""
    # 测试代码
```

### 文档规范

- 为新功能添加文档
- 更新README.md（如果需要）
- 更新CHANGELOG.md
- 添加代码注释（如果逻辑复杂）

## 开发环境

### 依赖

- Python 3.10+
- pytest
- Flask（Mock服务器）
- requests/httpx（HTTP客户端）

### 工具

- **pytest**: 测试框架
- **flake8**: 代码检查
- **mypy**: 类型检查
- **black**: 代码格式化
- **allure**: 测试报告

### 常用命令

```bash
# 安装依赖
poetry install

# 运行测试
pytest

# 运行E2E测试
pytest e2e/

# 运行性能测试
pytest performance/

# 运行代码检查
make lint

# 运行类型检查
make type-check

# 格式化代码
make format

# 运行所有检查
make check

# 生成测试报告
pytest --html=reports/report.html

# 生成Allure报告
pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report
```

## 项目结构

```
ai-gateway-test/
├── e2e/                    # E2E测试
├── performance/            # 性能测试
├── mock/                   # Mock服务器
├── utils/                  # 工具类
├── config/                 # 配置文件
├── docs/                   # 文档
│   ├── adr/                # 架构决策记录
│   └── agents/             # Agent技能配置
├── .github/                # GitHub配置
│   └── workflows/          # GitHub Actions
└── reports/                # 测试报告
```

## 发布流程

1. 更新版本号（pyproject.toml）
2. 更新CHANGELOG.md
3. 创建Git标签
4. 推送到GitHub
5. 创建GitHub Release

## 行为准则

- 尊重他人
- 接受建设性批评
- 专注于对社区最有利的事情
- 对他人表示同理心

## 问题反馈

如有任何问题，请通过以下方式联系：

- [GitHub Issues](https://github.com/chenzhiguo/ai-gateway-test/issues)
- [GitHub Discussions](https://github.com/chenzhiguo/ai-gateway-test/discussions)

感谢您的贡献！