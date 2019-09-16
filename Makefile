# some common operations

clean_dist:
	rm -rf dist *.egg-info

clean_tests:
	rm -rf .pytest_cache .tox
	py3clean .

clean_mypy:
	rm -rf .mypy_cache

clean: clean_dist clean_mypy clean_tests

test:
	tox

package: clean_dist
	python setup.py sdist

format:
	black .
