# Nifty100 ETL Pipeline

## Objective
Build an ETL pipeline for Nifty100 companies and generate analytical datasets.

## Project Structure
data/
src/
tests/
sql/
output/
notebooks/

## Components
- Loader
- Normalizer
- Validator
- Feature Engineering

## Outputs
- nifty100.db
- load_audit.csv
- validation_failures.csv
- company_kpis.csv
- company_growth.csv
- final_company_features.csv

## Tests
57 tests passing

## Technologies
Python
Pandas
SQLite
Pytest

## How to Run

python -m src.etl.preprocess

pytest
