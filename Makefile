# HueCIT Chatbot RAG - Makefile
# Quality commands and development workflow

.PHONY: help install lint format test check clean docs coverage security

# ==========================================
# Variables
# ==========================================
PYTHON := python3
VENV := venv
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy

# ==========================================
# Default target
# ==========================================
help:
	@echo "HueCIT Chatbot RAG - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies"
	@echo "  make install-dev    Install dev dependencies"
	@echo "  make setup          Full setup (install + hooks)"
	@echo ""
	@echo "Quality:"
	@echo "  make format         Format code (black + isort)"
	@echo "  make lint           Run linting (flake8)"
	@echo "  make type           Run type checking (mypy)"
	@echo "  make test           Run tests"
	@echo "  make coverage       Run tests with coverage"
	@echo "  make security       Run security scan"
	@echo "  make check          Run all quality checks"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Clean cache and build files"
	@echo "  make clean-all      Deep clean (including venv)"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           Build documentation"

# ==========================================
# Setup
# ==========================================
install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

setup: install install-dev
	pre-commit install
	@echo "✓ Setup complete! Run 'source venv/bin/activate' to activate."

# ==========================================
# Formatting
# ==========================================
format:
	$(BLACK) src tests
	$(ISORT) src tests
	@echo "✓ Code formatted"

format-check:
	$(BLACK) --check src tests
	$(ISORT) --check src tests

# ==========================================
# Linting
# ==========================================
lint:
	$(FLAKE8) src tests --max-line-length=100 --extend-ignore=E203,W503
	@echo "✓ Linting complete"

# ==========================================
# Type checking
# ==========================================
type:
	$(MYPY) src --ignore-missing-imports --no-strict-optional
	@echo "✓ Type checking complete"

# ==========================================
# Testing
# ==========================================
test:
	$(PYTEST) tests/ -v --tb=short
	@echo "✓ Tests complete"

test-week1:
	$(PYTEST) tests/week1/ -v

test-week2:
	$(PYTEST) tests/week2/ -v

test-week3:
	$(PYTEST) tests/week3/ -v

test-week4:
	$(PYTEST) tests/week4/ -v

test-week5:
	$(PYTEST) tests/week5/ -v

test-week6:
	$(PYTEST) tests/week6/ -v

test-week7:
	$(PYTEST) tests/week7/ -v

test-week8:
	$(PYTEST) tests/week8/ -v

# ==========================================
# Coverage
# ==========================================
coverage:
	$(PYTEST) tests/ --cov=src --cov-report=term-missing --cov-report=html
	@echo "✓ Coverage report generated in htmlcov/"

# ==========================================
# Security
# ==========================================
security:
	bandit -r src/ -ll --skip B101
	safety check --full-report
	@echo "✓ Security scan complete"

# ==========================================
# All checks
# ==========================================
check: format-check lint type test
	@echo "✓ All quality checks passed"

# ==========================================
# Cleanup
# ==========================================
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Cleaned cache files"

clean-all: clean
	rm -rf build/ dist/ .eggs/ htmlcov/ .coverage
	rm -rf $(VENV)
	@echo "✓ Deep clean complete"

# ==========================================
# Documentation
# ==========================================
docs:
	cd docs && make html
	@echo "✓ Documentation built"

# ==========================================
# Pre-commit
# ==========================================
pre-commit:
	pre-commit run --all-files
	@echo "✓ Pre-commit checks complete"

pre-commit-install:
	pre-commit install
	@echo "✓ Pre-commit hooks installed"