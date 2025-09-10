"""
Test database service for LazyAI Studio
"""

import pytest
from unittest.mock import Mock, patch
from app.core.database_service import DatabaseService, init_database_service, get_database_service


class TestDatabaseService:
    """Test DatabaseService class"""

    def test_database_service_initialization(self):
        """Test DatabaseService initialization"""
        service = DatabaseService()
        assert service.is_ready is False
        assert service.models_service is not None
        assert service.last_update is None

    def test_initialize_success(self):
        """Test successful database initialization"""
        service = DatabaseService()
        
        with patch.object(service.models_service, 'load_models') as mock_load:
            mock_load.return_value = None  # Successful load
            
            result = service.initialize()
            assert result is True
            assert service.is_ready is True
            assert service.last_update is not None
            mock_load.assert_called_once()

    def test_initialize_failure(self):
        """Test database initialization failure"""
        service = DatabaseService()
        
        with patch.object(service.models_service, 'load_models') as mock_load:
            mock_load.side_effect = Exception("Load failed")
            
            result = service.initialize()
            assert result is False
            assert service.is_ready is False

    def test_get_models(self, sample_model_data):
        """Test getting models from database service"""
        service = DatabaseService()
        service.is_ready = True
        
        with patch.object(service.models_service, 'get_models') as mock_get:
            mock_get.return_value = [sample_model_data]
            
            models = service.get_models()
            assert len(models) == 1
            assert models[0]["slug"] == "test-model"
            mock_get.assert_called_once()

    def test_get_models_not_ready(self):
        """Test getting models when service not ready"""
        service = DatabaseService()
        service.is_ready = False
        
        models = service.get_models()
        assert models == []

    def test_get_model_by_slug(self, sample_model_data):
        """Test getting model by slug"""
        service = DatabaseService()
        service.is_ready = True
        
        with patch.object(service.models_service, 'get_model_by_slug') as mock_get:
            mock_get.return_value = sample_model_data
            
            model = service.get_model_by_slug("test-model")
            assert model is not None
            assert model["slug"] == "test-model"
            mock_get.assert_called_once_with("test-model")

    def test_get_model_by_slug_not_ready(self):
        """Test getting model by slug when service not ready"""
        service = DatabaseService()
        service.is_ready = False
        
        model = service.get_model_by_slug("test-model")
        assert model is None

    def test_get_status(self):
        """Test getting database service status"""
        service = DatabaseService()
        service.is_ready = True
        service.models_service.models = [{"slug": "test"}]
        
        status = service.get_status()
        assert status["ready"] is True
        assert status["models_count"] == 1
        assert "last_update" in status

    def test_close(self):
        """Test closing database service"""
        service = DatabaseService()
        service.is_ready = True
        
        service.close()
        assert service.is_ready is False
        assert service.last_update is None

    def test_refresh(self):
        """Test refreshing database service"""
        service = DatabaseService()
        
        with patch.object(service, 'initialize') as mock_init:
            mock_init.return_value = True
            
            result = service.refresh()
            assert result is True
            mock_init.assert_called_once()


class TestDatabaseServiceModule:
    """Test module-level database service functions"""

    def test_init_database_service(self):
        """Test initializing database service"""
        with patch('app.core.database_service.DatabaseService') as mock_service_class:
            mock_service = Mock()
            mock_service.initialize.return_value = True
            mock_service_class.return_value = mock_service
            
            service = init_database_service()
            assert service is not None
            mock_service.initialize.assert_called_once()

    def test_init_database_service_failure(self):
        """Test database service initialization failure"""
        with patch('app.core.database_service.DatabaseService') as mock_service_class:
            mock_service = Mock()
            mock_service.initialize.return_value = False
            mock_service_class.return_value = mock_service
            
            with pytest.raises(RuntimeError, match="Failed to initialize database service"):
                init_database_service()

    def test_get_database_service_not_initialized(self):
        """Test getting database service when not initialized"""
        with patch('app.core.database_service._database_service', None):
            with pytest.raises(RuntimeError, match="Database service not initialized"):
                get_database_service()

    def test_get_database_service_initialized(self):
        """Test getting database service when initialized"""
        mock_service = Mock()
        with patch('app.core.database_service._database_service', mock_service):
            service = get_database_service()
            assert service == mock_service

    @patch('app.core.database_service._database_service', None)
    def test_database_service_singleton(self):
        """Test that database service is a singleton"""
        with patch('app.core.database_service.DatabaseService') as mock_service_class:
            mock_service = Mock()
            mock_service.initialize.return_value = True
            mock_service_class.return_value = mock_service
            
            # Initialize twice
            service1 = init_database_service()
            service2 = init_database_service()
            
            # Should return same instance
            assert service1 == service2
            # DatabaseService should only be called once
            mock_service_class.assert_called_once()


class TestDatabaseServiceErrors:
    """Test error handling in database service"""

    def test_database_service_exception_handling(self):
        """Test exception handling in database operations"""
        service = DatabaseService()
        service.is_ready = True
        
        with patch.object(service.models_service, 'get_models') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            # Should handle exception gracefully
            models = service.get_models()
            assert models == []

    def test_models_service_none(self):
        """Test behavior when models_service is None"""
        service = DatabaseService()
        service.models_service = None
        
        models = service.get_models()
        assert models == []
        
        model = service.get_model_by_slug("test")
        assert model is None

    def test_concurrent_initialization(self):
        """Test concurrent initialization handling"""
        service = DatabaseService()
        
        with patch.object(service.models_service, 'load_models') as mock_load:
            mock_load.return_value = None
            
            # Simulate concurrent initialization
            result1 = service.initialize()
            result2 = service.initialize()
            
            assert result1 is True
            assert result2 is True
            # Should only initialize once
            mock_load.assert_called_once()