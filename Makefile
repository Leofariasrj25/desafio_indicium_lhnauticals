.PHONY: setup eda transform

setup:
	@echo "Instalando dependências via poetry"
	poetry install

eda:
	@echo "Abrindo o relatório de análise explorátoria"
	poetry run jupyter notebook notebooks/01_eda_sales.ipynb
