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
	@cmd //c ".venv\Scripts\pytest tests integration"

watch:
	@cmd //c ".venv\Scripts\activate && ptw -- -vv -s tests"

# Novas regras adicionadas:
fmt:
	@echo "Formatando código..."
	@cmd //c ".venv\Scripts\black dundie/ tests/"
	@cmd //c ".venv\Scripts\isort dundie/ tests/"

lint:
	@echo "Verificando estilo de código..."
	@cmd //c ".venv\Scripts\flake8 dundie/ tests/"

check: fmt lint test
	@echo "✓ Todas as verificações passaram!"

.PHONY: install virtualenv init clean test watch fmt lint check