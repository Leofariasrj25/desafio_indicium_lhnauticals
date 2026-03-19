.PHONY: setup eda q02 

setup:
	@echo "Installing dependencies via poetry"
	poetry install

eda:
	@echo "Abrindo o relatório de análise explorátoria"
	poetry run jupyter notebook notebooks/01_eda_sales.ipynb

q02:
	@echo "q02 - Product Data Normalization"
	poetry run python src/q02_normalize_products.py

q03:
	@echo "q03 - Import costs flattening"
	poetry run python src/q03_flatten_imports.py

q04:
	@echo "q04 - Public Data"
	poetry run python src/q04_calculate_profitability.py

clean:
	@echo "Cleaning processed files"
	@rm -rf ./data/processed/*
