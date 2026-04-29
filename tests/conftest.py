"""
Shared pytest configuration and fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root):
    """Return data directory path."""
    return project_root / "data"


@pytest.fixture
def output_dir(project_root):
    """Return output directory path."""
    return project_root / "output"


@pytest.fixture
def temp_output_dir(tmp_path):
    """Return temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    return output_dir


@pytest.fixture
def sample_document():
    """Return sample document for testing."""
    return {
        "doc_id": "test-doc-001",
        "title": "Test Document",
        "content": "This is a test document content for testing purposes.",
        "parse_status": "success",
        "headings": [
            {"level": 1, "text": "Introduction"},
            {"level": 2, "text": "Background"}
        ]
    }


@pytest.fixture
def sample_screenshot_metadata():
    """Return sample screenshot metadata for testing."""
    return {
        "screen_id": "test-screen-001",
        "doc_id": "test-doc-001",
        "screen_type": "error",
        "domain_id": "D1",
        "function_area": "login",
        "error_codes": ["AUTH001"],
        "screen_context": "Login error screen",
        "ocr_ready": True
    }