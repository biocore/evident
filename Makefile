all: stylecheck test
test: standalone_test q2_test
stylecheck: standalone_stylecheck q2_stylecheck

standalone_stylecheck:
	flake8 evident/*.py
	flake8 evident/tests/*.py
	flake8 setup.py

q2_stylecheck:
	flake8 evident/q2/*.py
	flake8 evident/q2/tests/*.py

standalone_test:
	pytest --cov-report term-missing --cov=evident --cov-config=config/standalone_cov.ini evident/tests/ --cov-branch

q2_test:
	pytest --cov-report term-missing --cov=./evident/q2 --cov-config=config/q2_cov.ini evident/q2/tests/ --cov-branch
