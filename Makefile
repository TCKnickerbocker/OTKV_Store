.PHONY: clean run clean-run
clean:
	# Remove all log files in ./logs directory
	rm -f ./logs/*
	
	# Remove __pycache__ directories in the current directory and its subdirectories
	find . -type d -name "__pycache__" -exec rm -rf {} +
	
	# Remove .pyc files in kv_store
	find ./kv_store -type f -name "*.pyc" -delete
	
	# Remove .pyc files in the current directory and its subdirectories
	find . -type f -name "*.pyc" -delete
	# Remove dump file
	rm -f dump.rdb
# Runs with one node
run:
	python3 main.py
clean-run: clean run
