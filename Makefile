format:
	pre-commit run --all-files

docs_sautobuild:
	sphinx-autobuild docs docs/_build/html

publish:
	python3 -m build
	python3 -m twine upload --repository pypi dist/*