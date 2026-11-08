install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=greedy_lab --cov-report=term-missing

format:	
	black *.py greedy_lab/ tests/

lint:
	pylint --disable=R,C --ignore-patterns=test_.*?py *.py greedy_lab/*.py

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

refactor: format lint

deploy:
	#deploy goes here
		
all: install lint test format deploy