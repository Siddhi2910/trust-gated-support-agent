import os
import yaml
import pytest

def test_config_loads():
    """Verify that configs/base.yaml exists, is valid YAML, and contains required top-level keys."""
    config_path = os.path.join("configs", "base.yaml")
    assert os.path.exists(config_path), f"Configuration file not found at {config_path}"
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    assert isinstance(config, dict), "Parsed config must be a dictionary"
    assert "project" in config, "Missing 'project' section in config"
    assert "paths" in config, "Missing 'paths' section in config"
    assert config["project"].get("target_brand") == "AppleSupport", "target_brand must be AppleSupport"
    if not os.path.exists(config["paths"]["raw_dataset"]):
        pytest.skip(f"Raw dataset omitted from git: {config['paths']['raw_dataset']}")
    assert os.path.exists(config["paths"]["raw_dataset"])
