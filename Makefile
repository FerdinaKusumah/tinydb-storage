.PHONY: update install format lint test prerelease release build publish clean

update:
	poetry update

install:
	poetry install --all-extras

format:
	poetry run black .

lint:
	poetry run black --check .

test:
	poetry run pytest

prerelease:
	poetry version prerelease

release:
	poetry version patch

build:
	poetry build

publish:
	poetry publish --build --skip-existing

clean:
	rm -rf dist/ .coverage
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
