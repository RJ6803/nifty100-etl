install:
	pip install -r requirements.txt

test:
	pytest

kpi:
	python -m src.features.kpi_calculator

growth:
	python -m src.features.growth_metrics

features:
	python -m src.features.final_features