.PHONY: pipeline test dashboard

pipeline:
	python -m src.generate_data
	python -m src.etl
	python -m src.analysis

test:
	pytest -q

dashboard:
	streamlit run dashboard/app.py
