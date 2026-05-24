# AI Gateway测试项目Makefile

.PHONY: help install test test-e2e test-performance report clean

# 默认目标
help:
	@echo "AI Gateway测试项目"
	@echo ""
	@echo "可用命令:"
	@echo "  make install        安装依赖"
	@echo "  make test           运行所有测试"
	@echo "  make test-e2e       运行E2E测试"
	@echo "  make test-performance 运行性能测试"
	@echo "  make report         生成测试报告"
	@echo "  make clean          清理临时文件"
	@echo "  make mock           启动Mock服务器"

# 安装依赖
install:
	poetry install

# 运行所有测试
test:
	pytest -v --html=reports/report.html --self-contained-html --alluredir=reports/allure-results

# 运行E2E测试
test-e2e:
	pytest e2e/ -v --html=reports/e2e-report.html --self-contained-html

# 运行性能测试
test-performance:
	pytest performance/ -v --html=reports/performance-report.html --self-contained-html

# 运行冒烟测试
test-smoke:
	pytest -m smoke -v

# 运行回归测试
test-regression:
	pytest -m regression -v

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