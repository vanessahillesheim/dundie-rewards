install: 
	@echo "Instalando para desenvolvimento!"
	@cmd //c ".venv\Scripts\activate && pip install -e .[dev]"

virtualenv:
	@python -m venv .venv

init: virtualenv install

clean:
	@rmdir //s //q .venv 2>nul || exit 0
	@rmdir //s //q build 2>nul || exit 0
	@rmdir //s //q dist 2>nul || exit 0
	@rmdir //s //q *.egg-info 2>nul || exit 0

test:
	@cmd //c ".venv\Scripts\activate && pytest"

watch:
	@cmd //c ".venv\Scripts\activate\ptw -- -vv -s -tests"

.PHONY: install virtualenv init clean test