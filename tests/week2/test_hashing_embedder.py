import numpy as np
import pytest

from src.week2.vector_index import HashingTextEmbedder


def test_hashing_text_embedder_is_deterministic():
    embedder = HashingTextEmbedder(dimension=32)

    first = embedder.encode(["dang nhap he thong", "ket noi database"])
    second = embedder.encode(["dang nhap he thong", "ket noi database"])

    assert first.shape == (2, 32)
    assert np.array_equal(first, second)
    assert first.sum() > 0


def test_hashing_text_embedder_rejects_invalid_dimension():
    with pytest.raises(ValueError, match="dimension must be positive"):
        HashingTextEmbedder(dimension=0)
