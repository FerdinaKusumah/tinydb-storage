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

build:
	poetry build

publish:
	poetry publish --build --skip-existing
