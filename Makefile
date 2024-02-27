format:
	pre-commit run --all-files

docs_autobuild:
	sphinx-autobuild -E docs docs/_build/html
	
docs_test:
	sphinx-build docs docs/_build/html -b doctest

publish:
	python3 -m build
	python3 -m twine upload --repository pypi dist/*