.PHONY: install run test clean format lint

# 安装依赖
install:
	pip install -e .

# 运行服务器
run:
	python run_server.py

# 测试API
test:
	python api_example.py

# 清理缓存文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# 代码格式化
format:
	ruff format .

# 代码检查
lint:
	ruff check .

# 开发模式（格式化 + 检查 + 运行）
dev: format lint run

