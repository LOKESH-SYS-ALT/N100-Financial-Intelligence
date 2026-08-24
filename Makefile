.PHONY: load ratios test report dashboard api clean

load:
	python -m src.etl.loader

ratios:
	python -m src.etl.ratios

test:
	pytest tests/etl -v

report:
	python -m src.etl.report

dashboard:
	streamlit run src/dashboard/app.py

api:
	python -m src.api

clean:
	python -m src.etl.clean