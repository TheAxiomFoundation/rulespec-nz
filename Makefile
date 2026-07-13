.PHONY: setup test lint format typecheck quality coverage scorecard clean

# ─── Setup ──────────────────────────────────────────────────────────────────

setup:
	pixi install

# ─── Testing ────────────────────────────────────────────────────────────────

test:
	pixi run test

test-unit:
	pixi run test-unit

test-integration:
	pixi run test-integration

test-e2e:
	pixi run test-e2e

# ─── Linting & Formatting ──────────────────────────────────────────────────

lint:
	pixi run lint

format:
	pixi run ruff format src tests test_bindings.py

format-check:
	pixi run format-check

typecheck:
	pixi run typecheck

# ─── Quality gate ──────────────────────────────────────────────────────────

quality: lint format-check typecheck test rust-test

# ─── Coverage ──────────────────────────────────────────────────────────────

coverage:
	pixi run pytest --cov=rulespec_nz --cov-report=html --cov-report=term

# ─── Scorecard ─────────────────────────────────────────────────────────────

scorecard:
	python scripts/phase4_scorecard.py

# ─── Rust ──────────────────────────────────────────────────────────────────

rust-test:
	pixi run rust-test

# ─── Cleanup ───────────────────────────────────────────────────────────────

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__
	find . -name '*.pyc' -delete
