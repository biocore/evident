all: stylecheck test
test: standalone_test q2_test

stylecheck:
	flake8 evident/*.py
	flake8 setup.py

standalone_test:
	pytest --cov-report term-missing --cov=evident --cov-config=config/standalone_cov.ini evident/tests/ --cov-branch

q2_test:
	pytest --cov-report term-missing --cov=./evident/q2 --cov-config=config/q2_cov.ini evident/q2/tests/ --cov-branch
