"""
Schema validation utilities for HueCIT Chatbot RAG data pipeline.

Provides functions to validate documents, screenshots, queries, and chunks
against their respective JSON schemas.
"""

import json
from pathlib import Path
from typing import Any, Optional

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "data" / "schemas"

SCHEMA_FILES = {
    "document": "document_metadata_schema.json",
    "screenshot": "screenshot_metadata_schema.json",
    "query": "query_schema.json",
    "ocr_ground_truth": "ocr_ground_truth_schema.json",
    "chunk": "chunk_metadata_schema.json",
    "domain_taxonomy": "domain_taxonomy.json",
}


def _load_schema(schema_name: str) -> dict:
    """Load a JSON schema from the schemas directory."""
    filename = SCHEMA_FILES.get(schema_name)
    if not filename:
        raise ValueError(f"Unknown schema: {schema_name}. Available: {list(SCHEMA_FILES.keys())}")

    schema_path = SCHEMAS_DIR / filename
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)


def validate_document(doc: dict) -> tuple[bool, Optional[str]]:
    """Validate a document against the document metadata schema.

    Returns (is_valid, error_message).
    """
    if not HAS_JSONSCHEMA:
        required = ["doc_id", "title", "content", "parse_status"]
        missing = [f for f in required if f not in doc]
        if missing:
            return False, f"Missing required fields: {missing}"
        return True, None

    schema = _load_schema("document")
    try:
        jsonschema.validate(doc, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)


def validate_screenshot(screen: dict) -> tuple[bool, Optional[str]]:
    """Validate a screenshot against the screenshot metadata schema."""
    if not HAS_JSONSCHEMA:
        required = ["screen_id", "doc_id", "screen_type", "source_path"]
        missing = [f for f in required if f not in screen]
        if missing:
            return False, f"Missing required fields: {missing}"
        return True, None

    schema = _load_schema("screenshot")
    try:
        jsonschema.validate(screen, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)


def validate_query(query: dict) -> tuple[bool, Optional[str]]:
    """Validate a query against the query schema."""
    if not HAS_JSONSCHEMA:
        required = ["query_id", "query_text"]
        missing = [f for f in required if f not in query]
        if missing:
            return False, f"Missing required fields: {missing}"
        return True, None

    schema = _load_schema("query")
    try:
        jsonschema.validate(query, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)


def validate_chunk(chunk: dict) -> tuple[bool, Optional[str]]:
    """Validate a chunk against the chunk metadata schema."""
    if not HAS_JSONSCHEMA:
        required = ["chunk_id", "doc_id", "chunk_order", "chunk_method", "chunk_text"]
        missing = [f for f in required if f not in chunk]
        if missing:
            return False, f"Missing required fields: {missing}"
        return True, None

    schema = _load_schema("chunk")
    try:
        jsonschema.validate(chunk, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e.message)


def load_domain_taxonomy() -> list[dict]:
    """Load the domain taxonomy (D1-D7)."""
    data = _load_schema("domain_taxonomy")
    return data.get("domains", [])


def validate_batch(
    items: list[dict], validator_func: callable
) -> tuple[list[dict], list[dict]]:
    """Validate a batch of items. Returns (valid_items, invalid_items_with_errors).

    Each invalid item gets an '_validation_error' field added.
    """
    valid, invalid = [], []
    for item in items:
        is_valid, error = validator_func(item)
        if is_valid:
            valid.append(item)
        else:
            item["_validation_error"] = error
            invalid.append(item)
    return valid, invalid
