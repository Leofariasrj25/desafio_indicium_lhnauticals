.PHONY: help setup etl q02 q03 q04 eda report lab clean

# ==========================================
# ENVIRONMENT VARIABLES
# ==========================================
POETRY_RUN = poetry run
PYTHON = $(POETRY_RUN) python
JUPYTER = $(POETRY_RUN) jupyter notebook
ETL_DIR = src/etl
NB_DIR = notebooks
REPORT_DIR = reports

# ==========================================
# HELP MENU (Default Command)
# ==========================================
help:
	@echo "======================================================================"
	@echo " LH Nauticals - Data Pipeline"
	@echo "======================================================================"
	@echo "Available Commands:"
	@echo "  make setup   - Install all project dependencies via Poetry"
	@echo "  make etl     - Run the complete data pipeline (q02 -> q03 -> q04)"
	@echo "  make lab     - Open the Jupyter Notebook environment in the project folder"
	@echo "  make eda     - Open the Exploratory Data Analysis notebook directly (Q01)"
	@echo "  make report  - Open the Consolidated Final Report directly"
	@echo "  make html    - Convert the Consolidated Final Report into a HTML page"
	@echo "  make clean   - Clean processed data and Python cache files"
	@echo "======================================================================"

# ==========================================
# SETUP
# ==========================================
setup:
	@echo "==> Installing dependencies..."
	poetry install

# ==========================================
# ETL PIPELINE (Data Processing)
# ==========================================
etl: products imports clients 
	@echo "==> ETL pipeline finished successfully. Data ready in data/processed/"

products:
	@echo "==> Q02: Normalizing product catalog..."
	@$(PYTHON) $(ETL_DIR)/q02_normalize_products.py

imports:
	@echo "==> Q03: Flattening import cost data..."
	@$(PYTHON) $(ETL_DIR)/q03_flatten_imports.py

clients:
	@echo "==> Extra: Flattening and normalizing client data..."
	$(PYTHON) $(ETL_DIR)/client_flattening_normalization.py

# ==========================================
# ANALYSIS AND PRESENTATION (Notebooks)
# ==========================================
lab:
	@echo "==> Starting Jupyter Server..."
	@$(JUPYTER) $(NB_DIR)/

eda:
	@echo "==> Opening the Exploratory Data Analysis (EDA) report..."
	@$(JUPYTER) $(NB_DIR)/01_eda_sales.ipynb

report:
	@echo "==> Opening the Final Executive Report..."
	@$(JUPYTER) $(NB_DIR)/final_report_lhnauticals.ipynb

html:
	@echo "==> Exporting the Final Executive Report to a HTML file..."
	@mkdir -p report
	@$(POETRY_RUN) jupyter nbconvert --to html $(NB_DIR)/final_report_lhnauticals.ipynb --output-dir $(REPORT_DIR) 
	@echo "==> Report sucessfully converted and saved at $(REPORT_DIR)/"

# ==========================================
# MAINTENANCE
# ==========================================
clean:
	@echo "==> Cleaning output directories..."
	@rm -rf ./data/processed/*
	@rm -rf ./processed/*
	@rm -rf ./reports/*
	@echo "==> Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "==> Environment clean."
