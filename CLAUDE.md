# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LazyAI Studio** - LazyGophers 组织出品的 AI 智能工作室。这是一个专为懒人开发者设计的综合性 AI 开发解决方案，通过智能模式、个性角色和便捷命令，让复杂的开发工作变得简单高效。

项目包含完整的前后端应用：后端基于 FastAPI 提供 REST API，前端使用 React + TypeScript + Ant Design 构建现代化管理界面，为开发者提供直观的 AI 模式配置和管理体验。

## Commands

### Development & Testing
```bash
# Install all dependencies (frontend + backend)
make install

# Development servers
make dev                   # Start full-stack dev environment
make backend-dev          # Start backend only (port 8000)
make backend-dev-optimized # Start high-performance backend (ultra cache)
make frontend-dev         # Start frontend only (port 3000)

# Production
make run                  # Build and start production server
make build               # Build frontend for production

# Testing
make test                # Run all tests (frontend + backend)
make test-backend        # Run Python backend tests only
make test-frontend       # Run React frontend tests only
make test-coverage       # Generate coverage reports
make test-watch          # Run tests in watch mode

# Performance
make benchmark           # Run performance comparison tests
make benchmark-optimized # Test ultra-performance version

# Maintenance
make clean              # Clean all build files
make clean-frontend     # Clean frontend build only
```

### Single Test Examples
```bash
# Backend single test
uv run pytest tests/test_api_endpoints.py::test_health_check -v

# Frontend single test
cd frontend && npm test -- --testNamePattern="App renders"

# Integration test
uv run pytest tests/test_integration_comprehensive.py -v
```

## Architecture

### Full-Stack Architecture

```
LazyAI Studio
├── Backend (FastAPI)
│   ├── app/main.py              # Main application entry
│   ├── app/main_ultra.py        # Ultra-performance variant
│   ├── app/core/                # Core services
│   │   ├── database_service.py  # Main data management
│   │   ├── database_service_lite.py # Performance-optimized
│   │   ├── ultra_cache_system.py # Multi-level caching
│   │   └── secure_logging.py    # Security-hardened logging
│   ├── app/routers/            # API endpoints
│   └── app/models/             # Data models
└── Frontend (React + TypeScript)
    ├── src/pages/              # Page components
    ├── src/components/         # Reusable components
    ├── src/contexts/           # React contexts (theme, etc)
    └── src/api/               # API client layer
```

### Core Backend Services

1. **Database Service** (`app/core/database_service.py`)
   - File-based data management with TinyDB
   - Real-time file watching with watchdog
   - YAML parsing and validation
   - Caching layer for performance

2. **Ultra Cache System** (`app/core/ultra_cache_system.py`) 
   - Multi-level caching (L1/L2/L3 + disk)
   - LRU cache with TTL support
   - Memory pool management
   - Performance optimization for high-load scenarios

3. **Secure Logging** (`app/core/secure_logging.py`)
   - Log injection prevention (CWE-117)
   - Input sanitization utilities
   - Safe key-value logging formatters

### Frontend Architecture

1. **React Application** (`frontend/src/`)
   - TypeScript for type safety
   - Ant Design component library
   - Multiple theme support (9 built-in themes)
   - Responsive design

2. **Key Components**
   - System monitoring with real-time metrics
   - Configuration management interface
   - Theme switching capabilities
   - Performance-optimized rendering

### Performance Variants

The system includes multiple performance tiers:
- **Standard** (`main.py`): Full-featured with file watching
- **Ultra** (`main_ultra.py`): Maximum performance with aggressive caching
- **Lite** (`database_service_lite.py`): Minimal resource usage

## Development Guidelines

### Security Requirements
- Use `app/core/secure_logging.py` for all user input logging
- All log statements must sanitize user-controlled data
- Follow CWE-117 prevention guidelines

### Performance Optimization
- Reference `PERFORMANCE_OPTIMIZATION.md` for optimization techniques
- Use appropriate service variant based on requirements
- Implement caching for frequently accessed data
- Monitor memory usage in production

### Frontend Development
```bash
cd frontend
npm start        # Development server
npm test         # Run tests
npm run build    # Production build
npm audit        # Security audit
```

### Testing Strategy
- **Unit Tests**: Individual function testing
- **Integration Tests**: Full API endpoint testing
- **Frontend Tests**: React component testing
- **Performance Tests**: Benchmark comparisons

### Technology Stack
- **Python**: 3.12+ with UV package manager
- **Backend**: FastAPI, TinyDB, Uvicorn, PyYAML
- **Performance**: psutil, orjson, uvloop for optimization  
- **Frontend**: React 19, TypeScript, Ant Design 5
- **Security**: Input sanitization, log injection prevention
- **Testing**: pytest (backend), Jest (frontend)
- **Development**: Hot reload, file watching, auto-testing

### Code Structure Conventions
- Backend follows FastAPI patterns with dependency injection
- Frontend uses React functional components with hooks
- Shared TypeScript interfaces between frontend/backend
- Modular component architecture with clear separation of concerns