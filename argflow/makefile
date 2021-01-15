clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-inf
	find . -depth -name __pycache__ -exec rm -rf {} \;

install: clean
	pip3 install .

test: clean
	coverage run --source=argflow -m unittest discover
	coverage report