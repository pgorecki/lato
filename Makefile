format:
	pre-commit run --all-files
	
test:
	pytest
	mypy lato
	pytest --doctest-modules lato

docs_autobuild:
	sphinx-autobuild --watch lato -E docs docs/_build/html
	
docs_test:
	sphinx-build docs docs/_build/html -b doctest
	
docs_pre_publish:
	poetry export --with dev --without examples --without-hashes -f requirements.txt --output docs/requirements.txt

publish:
	python3 -m build
	python3 -m twine upload --config-file .pypirc --repository pypi dist/*