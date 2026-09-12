import os

def test_required_directories_exist():
    """Assert that all required directories from the master specification exist."""
    required_dirs = [
        "configs",
        "data/raw",
        "data/interim",
        "data/processed",
        "src/data",
        "src/conversations",
        "src/taxonomy",
        "src/retrieval",
        "src/trust",
        "src/generation",
        "src/evaluation",
        "src/safety",
        "src/utils",
        "tests",
        "app",
        "scripts",
        "artifacts",
        "reports",
        "docs",
    ]
    for d in required_dirs:
        assert os.path.isdir(d), f"Required directory '{d}' is missing from the repository."

def test_placeholder_readmes_exist():
    """Assert that deferred modules contain explicit placeholder documentation."""
    deferred_modules = [
        "src/taxonomy",
        "src/retrieval",
        "src/trust",
        "src/generation",
        "src/evaluation",
        "src/safety",
        "src/utils",
        "app",
    ]
    for m in deferred_modules:
        readme_path = os.path.join(m, "README.md")
        assert os.path.exists(readme_path), f"Placeholder README missing in '{m}'"
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            assert "later phase" in content, f"Placeholder in '{m}' must state 'later phase'"

def test_raw_dataset_exists_and_non_empty():
    """Confirm twcs.csv is present in data/raw/ and is non-empty."""
    raw_path = os.path.join("data", "raw", "twcs.csv")
    assert os.path.isfile(raw_path), f"Expected raw dataset at '{raw_path}'"
    assert os.path.getsize(raw_path) > 100_000_000, f"Raw dataset appears truncated or empty: {os.path.getsize(raw_path)} bytes"

def test_gitignore_covers_sensitive_and_raw_data():
    """Assert .gitignore correctly protects secrets, data/raw, and generated outputs."""
    assert os.path.isfile(".gitignore"), ".gitignore file must exist"
    with open(".gitignore", "r", encoding="utf-8") as f:
        content = f.read()
    assert ".env" in content
    assert "data/raw" in content
    assert "node_modules" in content
