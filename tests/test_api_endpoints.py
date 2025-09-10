"""
Test API endpoints for LazyAI Studio
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app


class TestAPIEndpoints:
    """Test class for API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint_with_frontend(self, client):
        """Test root endpoint when frontend is built"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            response = client.get("/")
            # Should serve static files or return frontend content
            assert response.status_code in [200, 404]  # 404 is acceptable if no static files

    def test_root_endpoint_without_frontend(self, client):
        """Test root endpoint when frontend is not built"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "LazyAI Studio API is running"
            assert data["organization"] == "LazyGophers"
            assert data["mode"] == "development"
            assert data["frontend_status"] == "not_built"

    def test_models_list_endpoint(self, client, mock_database_service):
        """Test models list endpoint"""
        # Mock database service response
        mock_database_service.get_models.return_value = [
            {
                "slug": "test-model",
                "name": "Test Model",
                "roleDefinition": "Test role",
                "whenToUse": "For testing",
                "description": "Test description",
                "groups": ["test"],
                "file_path": "/test/path"
            }
        ]
        
        response = client.post("/api/models", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 1
        assert len(data["data"]) == 1
        # Should exclude customInstructions field
        assert "customInstructions" not in data["data"][0]

    def test_model_by_slug_endpoint(self, client, mock_database_service, sample_model_data):
        """Test get model by slug endpoint"""
        mock_database_service.get_model_by_slug.return_value = sample_model_data
        
        response = client.post("/api/models/by-slug", json={"slug": "test-model"})
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-model"
        assert data["name"] == "Test Model"

    def test_model_by_slug_not_found(self, client, mock_database_service):
        """Test get model by slug when model not found"""
        mock_database_service.get_model_by_slug.return_value = None
        
        response = client.post("/api/models/by-slug", json={"slug": "nonexistent"})
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()

    def test_models_categories_endpoint(self, client, mock_database_service):
        """Test models categories endpoint"""
        # Mock models with different groups
        mock_models = [
            {"slug": "model1", "groups": ["core"], "name": "Model 1"},
            {"slug": "model2", "groups": ["coder"], "name": "Model 2"},
            {"slug": "model3", "groups": ["core", "coder"], "name": "Model 3"}
        ]
        mock_database_service.get_models.return_value = mock_models
        
        response = client.post("/api/models/categories/list")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        categories = data["data"]
        assert "core" in categories
        assert "coder" in categories
        assert len(categories["core"]) >= 1
        assert len(categories["coder"]) >= 1

    def test_hooks_endpoints(self, client):
        """Test hooks endpoints"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.read_text') as mock_read:
            
            mock_exists.return_value = True
            mock_read.return_value = "# Test Hook Content"
            
            # Test before hook
            response = client.post("/api/hooks/before")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "before"
            
            # Test after hook
            response = client.post("/api/hooks/after")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "after"
            
            # Test all hooks
            response = client.post("/api/hooks")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "before" in data["data"]
            assert "after" in data["data"]

    def test_rules_endpoint(self, client):
        """Test rules endpoint"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.iterdir') as mock_iterdir:
            
            mock_exists.return_value = True
            mock_dir = Mock()
            mock_dir.is_dir.return_value = True
            mock_dir.name = "rules"
            mock_iterdir.return_value = [mock_dir]
            
            response = client.post("/api/rules")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total"] >= 0

    def test_commands_endpoint(self, client):
        """Test commands endpoint"""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.iterdir') as mock_iterdir:
            
            mock_exists.return_value = True
            mock_file = Mock()
            mock_file.is_file.return_value = True
            mock_file.name = "test_command.md"
            mock_file.stat.return_value.st_size = 100
            mock_file.stat.return_value.st_mtime = 1234567890
            mock_iterdir.return_value = [mock_file]
            
            response = client.post("/api/commands")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_invalid_request_body(self, client):
        """Test API endpoints with invalid request bodies"""
        # Test with invalid JSON
        response = client.post("/api/models", 
                             content="invalid json",
                             headers={"content-type": "application/json"})
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test endpoints that require specific fields"""
        # Test model by slug without slug field
        response = client.post("/api/models/by-slug", json={})
        assert response.status_code == 422

    @patch('app.core.database_service.get_database_service')
    def test_database_service_error(self, mock_get_service, client):
        """Test API behavior when database service fails"""
        # Mock service to raise an exception
        mock_service = Mock()
        mock_service.get_models.side_effect = Exception("Database error")
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/models", json={})
        # Should handle error gracefully
        assert response.status_code == 500