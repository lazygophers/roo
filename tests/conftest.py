"""
pytest configuration file for LazyAI Studio backend tests
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.core.config import PROJECT_ROOT
from app.core.database_service import get_database_service


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def temp_models_dir(tmp_path):
    """Create a temporary models directory with test data"""
    models_dir = tmp_path / "resources" / "models"
    models_dir.mkdir(parents=True)
    
    # Create test model file
    test_model = models_dir / "test-model.yaml"
    test_model.write_text("""
slug: test-model
name: Test Model
roleDefinition: A test model for unit testing
whenToUse: When running tests
description: Test model description
customInstructions: Test custom instructions
groups: [test]
""")
    
    return models_dir


@pytest.fixture
def temp_rules_dir(tmp_path):
    """Create a temporary rules directory with test data"""
    rules_dir = tmp_path / "resources" / "rules"
    rules_dir.mkdir(parents=True)
    
    # Create test rule file
    test_rule = rules_dir / "test-rule.md"
    test_rule.write_text("# Test Rule\n\nThis is a test rule.")
    
    return rules_dir


@pytest.fixture
def temp_commands_dir(tmp_path):
    """Create a temporary commands directory with test data"""
    commands_dir = tmp_path / "resources" / "commands"
    commands_dir.mkdir(parents=True)
    
    # Create test command file
    test_command = commands_dir / "test-command.md"
    test_command.write_text("# Test Command\n\n**Action**: Test command action")
    
    return commands_dir


@pytest.fixture
def mock_database_service():
    """Mock database service for testing"""
    with patch('app.core.database_service.get_database_service') as mock:
        service = Mock()
        service.is_ready = True
        service.get_models.return_value = []
        service.get_model_by_slug.return_value = None
        mock.return_value = service
        yield service


@pytest.fixture
def sample_model_data():
    """Sample model data for testing"""
    return {
        "slug": "test-model",
        "name": "Test Model",
        "roleDefinition": "A test model",
        "whenToUse": "For testing",
        "description": "Test description",
        "customInstructions": "Test instructions",
        "groups": ["test"],
        "file_path": "/test/path/model.yaml"
    }


@pytest.fixture
def sample_rule_metadata():
    """Sample rule metadata for testing"""
    return {
        "file_path": "/test/rules/test-rule.md",
        "source_directory": "rules",
        "file_size": 100,
        "last_modified": 1234567890
    }


@pytest.fixture
def sample_command_metadata():
    """Sample command metadata for testing"""
    return {
        "file_path": "/test/commands/test-command.md",
        "source_directory": "commands",
        "file_size": 200,
        "last_modified": 1234567891
    }


@pytest.fixture(autouse=True)
def cleanup_logs():
    """Clean up log files after each test"""
    yield
    # Clean up any test log files
    logs_dir = PROJECT_ROOT / "logs"
    if logs_dir.exists():
        for log_file in logs_dir.glob("test_*.log"):
            try:
                log_file.unlink()
            except FileNotFoundError:
                pass