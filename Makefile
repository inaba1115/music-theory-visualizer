# ---------------------------------------------------------------------
# Dev Targets
# ---------------------------------------------------------------------

.PHONY: all lint export_requirements

all: lint export_requirements

lint:
	uv run ruff check . --fix
	uv run ruff format .
	uv run ty check .

export_requirements:
	uv export --format requirements-txt --no-hashes > requirements.txt

# ---------------------------------------------------------------------
# App Targets
# ---------------------------------------------------------------------

.PHONY: streamlit

# Usage: make streamlit APP={STREAMLIT_SCRIPT.py}
streamlit:
	uv run streamlit run ${APP}
