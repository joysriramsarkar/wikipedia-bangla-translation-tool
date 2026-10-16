.PHONY: help clean test

help:
	@echo "Wikipedia Translation Toolkit"
	@echo "make clean   - Clean __pycache__ files"
	@echo "make test    - Run tests"

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
	find . -name "*.pyc" -delete 2>/dev/null
	find . -name "*.pyo" -delete 2>/dev/null

test:
	python run_all_tests.py
