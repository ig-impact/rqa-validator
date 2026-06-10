_default:
    @just --list

gen:
    uv run python docs/gen_rules.py

build: gen
    uv run zensical build --clean

serve: gen
    uv run zensical serve
