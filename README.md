# ⚓ LH Nautical: Data Analytics & Engineering Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Poetry](https://img.shields.io/badge/Poetry-Dependency_Manager-blueviolet)
![DuckDB](https://img.shields.io/badge/DuckDB-In--Process_OLAP-yellow)
![Status](https://img.shields.io/badge/Status-Completed-success)

## 📖 About the Project

This repository contains the end-to-end data engineering and analytics solution developed for the **Indicium Lighthouse Program**. The project addresses complex business challenges for **LH Nautical**, a premium nautical retailer, by transforming raw operational data into actionable strategic insights.

The core motivation of this project is to move beyond simple descriptive statistics and provide deep diagnostic and predictive analytics. By building a robust ETL pipeline and applying advanced analytical modeling, this project solves real-world business pains:
* **Profitability & Currency Risk:** Identifying products causing financial hemorrhage due to unadjusted USD/BRL exchange rates.
* **Customer Loyalty Profiling:** Segmenting elite customers based on diverse purchasing behaviors and high average order values.
* **Intelligent Cross-Selling:** Building a collaborative filtering recommendation engine ("*Who bought this, also bought...*") to maximize revenue without relying on expensive Big Data infrastructure.

## ✨ Key Features & Business Logic

* **SCD Type 2 Implementation in SQL:** Handled temporal exchange rate gaps (weekends/holidays) by building continuous validity windows (`valid_from` / `valid_to`) using ANSI SQL window functions, ensuring 100% data coverage for cost calculations.
* **Automated Data Quality:** Built Python ETL scripts to normalize product categories (removing spelling errors and duplicates) to ensure a single source of truth (*Golden Record*).
* **API Integration:** Dynamic extraction of historical USD/BRL exchange rates directly from the Central Bank of Brazil (BCB) API.
* **Recommendation System:** Implemented item-based collaborative filtering using Cosine Similarity to identify synergistic cross-sell opportunities (e.g., matching high-end GPS systems with premium outboard motors).

## 🗂️ Repository Structure

The project follows a modular, Medallion-inspired architecture for clear separation of concerns:

```text
.
├── data/
│   ├── raw/               # Bronze layer: Raw CSVs and JSONs (immutable)
│   └── processed/         # Silver layer: Cleaned, deduplicated, and normalized data
├── notebooks/             # Exploratory Data Analysis and specific challenge solutions
├── reports/               # Final deliverables (e.g., HTML/PDF generated reports)
├── src/
│   ├── etl/               # Python scripts for data transformation (Clean, Flatten, Calculate)
│   ├── services/          # External integrations (e.g., BCB API wrapper)
│   └── utils/             # Helper functions (e.g., Data loaders)
├── Makefile               # Automation commands (e.g., rendering reports)
├── pyproject.toml         # Poetry configuration and dependencies
└── README.md
```

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Package Management:** Poetry
* **Data Processing & SQL:** DuckDB, Pandas, NumPy
* **Data Visualization:** Plotly Express, Plotly Graph Objects
* *Machine Learning:** Scikit-learn (Cosine Similarity)
* **Automation:** Make / Jupyter nbconvert

---

## 🚀 How to Run the Project

### 1. Prerequisites
Ensure you have **Python 3.11+**, **Poetry**, and **Make** installed on your machine.

### 2. Installation
Clone the repository and install the dependencies using `Makefile`:

```bash
git clone [https://github.com/your-username/lh-nautical-analytics.git](https://github.com/your-username/lh-nautical-analytics.git)
cd lh-nautical-analytics

# Installs all dependencies via Poetry (poetry install also works)
make install

```

### 3. Running the ETL Pipeline
To process the raw data and generate the clean datasets in the `data/processed/` folder, use the Make rule:

```bash
# Runs the entire data transformation pipeline
make etl
```

### 4. Exploring the Notebooks
To launch the interactive environment and explore the exploratory data analysis and specific challenge solutions:

```bash
make lab
```

### 5. Generating the Final Report
To automatically generate a standalone HTML version of the final business report (with interactive Plotly charts):

```bash
make html
```

The output will be successfully generated and saved in the `reports/` directory as `final_report_lhnauticals.html.`

## ✍️ Author

**Leonardo Farias dos Santos**
* "Born to Code, Human After All" 
* [LinkedIn](https://www.linkedin.com/in/leofariasrj25/) | [GitHub](https://github.com/Leofariasrj25)
