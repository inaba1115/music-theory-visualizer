# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PIXI_RUN := uv run

# ---------------------------------------------------------------------
# Dev Targets
# ---------------------------------------------------------------------

.PHONY: all lint test

all: lint test

lint:
	$(PIXI_RUN) ruff check . --fix
	$(PIXI_RUN) ruff format .
	$(PIXI_RUN) ty check .

test:
	$(PIXI_RUN) pytest tests

# ---------------------------------------------------------------------
# Notebook Targets
# ---------------------------------------------------------------------

.PHONY: jupyter, marimo, streamlit

jupyter:
	$(PIXI_RUN) jupyter lab

# Usage: make marimo APP={MARIMO_SCRIPT.py}
marimo:
	$(PIXI_RUN) marimo edit ${APP}

# Usage: make streamlit APP={STREAMLIT_SCRIPT.py}
streamlit:
	$(PIXI_RUN) streamlit run ${APP}
