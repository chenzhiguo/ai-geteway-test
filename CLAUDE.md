# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

AI Gateway自动化测试项目，用于测试类似于OpenRouter的大模型代理网关。

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
└── reports/                # 测试报告
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行E2E测试
pytest e2e/

# 运行性能测试
pytest performance/

# 运行冒烟测试
pytest -m smoke
```

### 生成报告

```bash
# 生成HTML报告
pytest --html=reports/report.html

# 生成Allure报告
pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report
```

### 依赖管理

使用Poetry管理依赖：

```bash
# 安装依赖
poetry install

# 添加依赖
poetry add <package>
```

## Agent skills

### Issue tracker

GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo. See `docs/agents/domain.md`.