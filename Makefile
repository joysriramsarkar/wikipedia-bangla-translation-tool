.PHONY: help clean test run serve

help:
	@echo "Wikipedia Translation Toolkit"
	@echo "make run     - Run web dashboard (Flask app)"
	@echo "make serve   - Run web dashboard (built-in server)"
	@echo "make clean   - Clean __pycache__ files"
	@echo "make test    - Run tests"

run:
	python app.py

serve:
	python cx_postprocess/server.py

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
	find . -name "*.pyc" -delete 2>/dev/null
	find . -name "*.pyo" -delete 2>/dev/null

test:
	python run_all_tests.py
