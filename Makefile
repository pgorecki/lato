format:
	pre-commit run --all-files

publish:
	python3 -m build
	python3 -m twine upload --repository pypi dist/*