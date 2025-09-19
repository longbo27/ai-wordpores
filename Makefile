.PHONY: install run lint fmt

install:
poetry install

run:
poetry run longbo start --now

lint:
poetry run python -m compileall autobot

fmt:
poetry run black autobot
