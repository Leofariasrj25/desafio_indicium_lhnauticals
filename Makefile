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

clean:
	@echo "Cleaning processed files"
	@rm -rf ./data/processed/*
