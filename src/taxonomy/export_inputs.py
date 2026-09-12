"""Re-export from src.export_inputs for backward compatibility."""

from src.export_inputs import (
    EXPLICIT_STOPWORDS,
    STOPWORDS_SET,
    normalize_for_deduplication,
    tokenize_for_keywords,
    export_taxonomy_sample,
    compute_keyword_frequencies,
    compute_length_statistics
)

__all__ = [
    "EXPLICIT_STOPWORDS",
    "STOPWORDS_SET",
    "normalize_for_deduplication",
    "tokenize_for_keywords",
    "export_taxonomy_sample",
    "compute_keyword_frequencies",
    "compute_length_statistics"
]
