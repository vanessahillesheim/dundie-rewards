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

# Regra principal de teste - executa todos os testes
test:
	@echo "Executando todos os testes..."
	@cmd //c ".venv\\Scripts\\pytest tests/ -v --disable-warnings"

# Executar testes com cobertura
test-cov:
	@echo "Executando testes com cobertura..."
	@cmd //c ".venv\\Scripts\\pytest tests/ -v --cov=dundie --cov-report=html --disable-warnings"

# Executar apenas test_add.py
test-add:
	@echo "Executando test_add.py..."
	@cmd //c ".venv\\Scripts\\pytest tests/test_add.py -v --disable-warnings"

# Executar apenas test_database.py
test-database:
	@echo "Executando test_database.py..."
	@cmd //c ".venv\\Scripts\\pytest tests/test_database.py -v --disable-warnings"

# Executar apenas test_load.py
test-load:
	@echo "Executando test_load.py..."
	@cmd //c ".venv\\Scripts\\pytest tests/test_load.py -v --disable-warnings"

# Executar apenas test_read.py
test-read:
	@echo "Executando test_read.py..."
	@cmd //c ".venv\\Scripts\\pytest tests/test_read.py -v --disable-warnings"

# Watch mode para desenvolvimento
watch:
	@cmd //c ".venv\\Scripts\\activate && ptw -- -vv -s tests"

# Formatação de código
fmt:
	@echo "Formatando código..."
	@cmd //c ".venv\\Scripts\\black dundie/ tests/"
	@cmd //c ".venv\\Scripts\\isort dundie/ tests/"

# Verificação de estilo
lint:
	@echo "Verificando estilo de código..."
	@cmd //c ".venv\\Scripts\\flake8 dundie/ tests/"

# Check completo (formatação, lint e testes)
check: fmt lint test
	@echo "✓ Todas as verificações passaram!"

# Build do pacote
build:
	@python setup.py sdist bdist_wheel

.PHONY: install virtualenv init clean test test-cov test-add test-database test-load test-read watch fmt lint check build