# AI Gateway测试项目Makefile

.PHONY: help install test test-e2e test-smoke test-mock test-gw test-performance report clean

PYTEST := ./venv/bin/pytest

# 默认目标
help:
	@echo "AI Gateway测试项目"
	@echo ""
	@echo "可用命令:"
	@echo "  make install        安装依赖"
	@echo "  make test           运行所有测试"
	@echo "  make test-e2e       运行E2E测试"
	@echo "  make test-smoke     运行冒烟测试"
	@echo "  make test-mock      运行Mock服务器测试"
	@echo "  make test-gw        测试远程Gateway (需设置 GATEWAY_URL)"
	@echo "  make test-performance 运行性能测试"
	@echo "  make report         生成测试报告"
	@echo "  make clean          清理临时文件"

# 安装依赖
install:
	poetry install

# 运行所有测试
test:
	$(PYTEST) -v --html=reports/report.html --self-contained-html --alluredir=reports/allure-results

# 运行E2E测试
test-e2e:
	$(PYTEST) e2e/ -v --html=reports/e2e-report.html --self-contained-html

# 运行性能测试
test-performance:
	$(PYTEST) performance/ -v --html=reports/performance-report.html --self-contained-html

# 运行冒烟测试
test-smoke:
	$(PYTEST) -m smoke -v

# 运行Mock服务器测试
test-mock:
	$(PYTEST) tests/test_mock_server.py -v

# 测试远程Gateway
test-gw:
ifndef GATEWAY_URL
	$(error GATEWAY_URL is not set. Usage: make test-gw GATEWAY_URL=http://your-gateway:port)
endif
	$(PYTEST) e2e/ -v

# 运行回归测试
test-regression:
	$(PYTEST) -m regression -v

# 生成测试报告
report:
	allure generate reports/allure-results -o reports/allure-report --clean
	@echo "报告已生成: reports/allure-report/index.html"

# 打开测试报告
open-report:
	allure open reports/allure-report

# 启动Mock服务器
mock:
	python -m mock.common_server

# 清理临时文件
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf reports/
	rm -rf logs/
	rm -rf allure-results/
	rm -rf allure-report/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 代码检查
lint:
	flake8 e2e/ performance/ mock/ utils/ --max-line-length=120

# 格式化代码
format:
	black e2e/ performance/ mock/ utils/ --line-length=120

# 类型检查
type-check:
	mypy e2e/ performance/ mock/ utils/

# 运行所有检查
check: lint type-check test