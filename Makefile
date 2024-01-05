update:
	poetry update

install:
	poetry install

test:
	poetry run pytest --disable-warnings

prerelease:
	poetry version prerelease

release:
	poetry version patch

test-publish:
	poetry publish --build -r test-pypi

publish:
	poetry publish --build --skip-existing
