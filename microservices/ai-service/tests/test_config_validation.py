import os
import pytest
from ai_service.config_validation import validate_config

def test_missing_required_env(monkeypatch):
    monkeypatch.delenv('DEEPSEEK_API_KEY', raising=False)
    monkeypatch.setenv('DB_NAME', 'testdb')
    monkeypatch.setenv('DB_USER', 'testuser')
    monkeypatch.setenv('DB_PASSWORD', 'testpass')
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_PORT', '5432')
    with pytest.raises(ValueError):
        validate_config()

def test_invalid_env(monkeypatch):
    monkeypatch.setenv('DEEPSEEK_API_KEY', '')
    monkeypatch.setenv('DB_NAME', '')
    monkeypatch.setenv('DB_USER', '')
    monkeypatch.setenv('DB_PASSWORD', '')
    monkeypatch.setenv('DB_HOST', '')
    monkeypatch.setenv('DB_PORT', '')
    with pytest.raises(ValueError):
        validate_config() 