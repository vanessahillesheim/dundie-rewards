install: 
	@echo "Instalando para desenvolvimento!"
	@.venv\Scripts\pip install -e .[dev]

virtualenv:
	@python -m venv .venv

lint:
	@.venv\Scripts\python -m pflake8

init: virtualenv install

clean:
	@rmdir /s /q .venv 2>nul || exit 0
	@rmdir /s /q build 2>nul || exit 0
	@rmdir /s /q dist 2>nul || exit 0
	@rmdir /s /q *.egg-info 2>nul || exit 0

test:
	@.venv\Scripts\python -m pytest -v

watch:
	@.venv\Scripts\ptw -- -vv -s tests

.PHONY: install virtualenv init clean test watch pflake8