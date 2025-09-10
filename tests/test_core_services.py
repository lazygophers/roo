"""
Test core services for LazyAI Studio
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml

from app.core.models_service import ModelsService
from app.core.rules_service import RulesService
from app.core.commands_service import CommandsService


class TestModelsService:
    """Test ModelsService class"""

    def test_models_service_initialization(self, temp_models_dir):
        """Test ModelsService initialization"""
        with patch('app.core.config.PROJECT_ROOT', temp_models_dir.parent):
            service = ModelsService()
            assert service.models_dir == temp_models_dir
            assert service.models == []

    def test_load_models_success(self, temp_models_dir):
        """Test successful model loading"""
        with patch('app.core.config.PROJECT_ROOT', temp_models_dir.parent):
            service = ModelsService()
            service.load_models()
            
            assert len(service.models) == 1
            model = service.models[0]
            assert model["slug"] == "test-model"
            assert model["name"] == "Test Model"

    def test_load_models_invalid_yaml(self, temp_models_dir):
        """Test model loading with invalid YAML"""
        # Create invalid YAML file
        invalid_model = temp_models_dir / "invalid.yaml"
        invalid_model.write_text("invalid: yaml: content:")
        
        with patch('app.core.config.PROJECT_ROOT', temp_models_dir.parent):
            service = ModelsService()
            service.load_models()
            # Should skip invalid files and load valid ones
            assert len(service.models) == 1  # Only the valid test-model

    def test_get_models_filtering(self, temp_models_dir, sample_model_data):
        """Test model filtering functionality"""
        with patch('app.core.config.PROJECT_ROOT', temp_models_dir.parent):
            service = ModelsService()
            service.models = [sample_model_data]
            
            # Test category filtering
            filtered = service.get_models(category="test")
            assert len(filtered) == 1
            
            # Test search filtering
            filtered = service.get_models(search="Test")
            assert len(filtered) == 1
            
            # Test non-matching filter
            filtered = service.get_models(category="nonexistent")
            assert len(filtered) == 0

    def test_get_model_by_slug(self, temp_models_dir, sample_model_data):
        """Test getting model by slug"""
        with patch('app.core.config.PROJECT_ROOT', temp_models_dir.parent):
            service = ModelsService()
            service.models = [sample_model_data]
            
            # Test existing model
            model = service.get_model_by_slug("test-model")
            assert model is not None
            assert model["slug"] == "test-model"
            
            # Test non-existing model
            model = service.get_model_by_slug("nonexistent")
            assert model is None


class TestRulesService:
    """Test RulesService class"""

    def test_rules_service_initialization(self, temp_rules_dir):
        """Test RulesService initialization"""
        with patch('app.core.config.PROJECT_ROOT', temp_rules_dir.parent):
            service = RulesService()
            assert service.resources_dir == temp_rules_dir

    def test_get_available_rules_directories(self, temp_rules_dir):
        """Test getting available rules directories"""
        # Create multiple rules directories
        (temp_rules_dir.parent / "rules-code").mkdir()
        (temp_rules_dir.parent / "rules-python").mkdir()
        
        with patch('app.core.config.PROJECT_ROOT', temp_rules_dir.parent):
            service = RulesService()
            directories = service.get_available_rules_directories()
            
            # Should find at least the base rules directory
            assert len(directories) >= 1
            assert any("rules" in str(d) for d in directories)

    def test_get_rules_by_slug(self, temp_rules_dir):
        """Test getting rules by model slug"""
        with patch('app.core.config.PROJECT_ROOT', temp_rules_dir.parent):
            service = RulesService()
            
            # Test with simple slug
            result = service.get_rules_by_slug("test")
            assert result["slug"] == "test"
            assert result["success"] is True
            
            # Test with complex slug
            result = service.get_rules_by_slug("code-python-ai")
            expected_dirs = ["rules-code-python-ai", "rules-code-python", "rules-code", "rules"]
            assert result["searched_directories"] == expected_dirs

    def test_get_files_from_directory(self, temp_rules_dir):
        """Test getting files from directory"""
        with patch('app.core.config.PROJECT_ROOT', temp_rules_dir.parent):
            service = RulesService()
            files = service._get_files_from_directory(temp_rules_dir, "rules")
            
            assert len(files) == 1
            file_info = files[0]
            assert file_info["file_path"].endswith("test-rule.md")
            assert file_info["source_directory"] == "rules"
            assert "file_size" in file_info
            assert "last_modified" in file_info


class TestCommandsService:
    """Test CommandsService class"""

    def test_commands_service_initialization(self, temp_commands_dir):
        """Test CommandsService initialization"""
        with patch('app.core.config.PROJECT_ROOT', temp_commands_dir.parent):
            service = CommandsService()
            assert service.commands_dir == temp_commands_dir

    def test_get_all_commands(self, temp_commands_dir):
        """Test getting all commands"""
        with patch('app.core.config.PROJECT_ROOT', temp_commands_dir.parent):
            service = CommandsService()
            commands = service.get_all_commands()
            
            assert commands["success"] is True
            assert commands["total"] == 1
            assert len(commands["data"]) == 1
            
            command = commands["data"][0]
            assert command["file_path"].endswith("test-command.md")
            assert "file_size" in command
            assert "last_modified" in command

    def test_get_commands_empty_directory(self):
        """Test getting commands from empty directory"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            service = CommandsService()
            commands = service.get_all_commands()
            
            assert commands["success"] is True
            assert commands["total"] == 0
            assert len(commands["data"]) == 0


class TestServiceIntegration:
    """Test service integration and error handling"""

    def test_service_error_handling(self):
        """Test service behavior with filesystem errors"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = PermissionError("Access denied")
            
            # Services should handle errors gracefully
            service = ModelsService()
            models = service.get_models()
            assert models == []

    def test_yaml_parsing_errors(self, temp_models_dir):
        """Test YAML parsing error handling"""
        # Create file with malformed YAML
        malformed_file = temp_models_dir / "malformed.yaml"
        malformed_file.write_text("slug: test\nname: [unclosed list")
        
        with patch('app.core.config.PROJECT_ROOT', temp_models_dir.parent):
            service = ModelsService()
            service.load_models()
            # Should continue processing other files
            assert len(service.models) == 1  # Only valid test-model

    def test_file_permissions(self, temp_rules_dir):
        """Test handling of file permission errors"""
        with patch('pathlib.Path.iterdir') as mock_iterdir:
            mock_iterdir.side_effect = PermissionError("Permission denied")
            
            with patch('app.core.config.PROJECT_ROOT', temp_rules_dir.parent):
                service = RulesService()
                result = service.get_rules_by_slug("test")
                
                # Should handle error gracefully
                assert result["success"] is True
                assert result["total"] == 0