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

# Run specific test categories using markers
uv run pytest tests/ -m "unit" -v          # Unit tests only
uv run pytest tests/ -m "integration" -v   # Integration tests only
uv run pytest tests/ -m "api" -v           # API tests only
uv run pytest tests/ -m "not slow" -v      # Exclude slow tests
```

## Architecture

### Full-Stack Architecture

```
LazyAI Studio
├── Backend (FastAPI)
│   ├── app/main.py              # Main application entry
│   ├── app/main_optimized.py    # Ultra-performance variant
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

4. **MCP Tools Service** (`app/core/mcp_tools_service.py`)
   - Model Context Protocol (MCP) tools integration
   - Dynamic tool registration and management
   - Supports GitHub API, web scraping, file operations

5. **Advanced Tool Chain** (`app/tools/`)
   - **GitHub Tools** (`github_tools.py`): Complete GitHub API integration with 34+ tools
   - **Web Scraping Tools** (`fetch_tools.py`): Content extraction and web scraping
   - **File Tools** (`file_tools.py`): Advanced file manipulation utilities
   - **Cache Tools** (`cache_tools.py`): Performance optimization caching

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
- **Ultra** (`main_optimized.py`): Maximum performance with aggressive caching
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
- **MCP Integration**: Model Context Protocol tools (mcp, fastmcp)
- **Web Tools**: aiohttp, aiofiles, beautifulsoup4 for web scraping

## Environment Configuration

LazyAI Studio supports flexible environment configuration through environment variables for different deployment scenarios.

### Supported Environment Types
- **local**: Local development environment (default) - allows all CORS origins, suitable for development
- **remote**: Remote deployment environment - configurable CORS security policies, suitable for production

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Environment type (local/remote) |
| `DEBUG` | `false` | Debug mode toggle |
| `LOG_LEVEL` | `INFO` | Log level (DEBUG/INFO/WARNING/ERROR) |
| `HOST` | `0.0.0.0` | Service bind address |
| `PORT` | `8000` | Service port |
| `CORS_ORIGINS` | `*` | CORS allowed origins (remote environment only) |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials (remote environment only) |
| `DATABASE_PATH` | `/app/data/lazyai.db` | Database file path |
| `CACHE_TTL` | `3600` | Cache expiration time (seconds) |

### Configuration Usage

1. **Copy configuration template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit configuration file**:
   ```bash
   vim .env  # Modify as needed
   ```

3. **Deploy with environment**:
   ```bash
   make docker-deploy  # Automatically reads .env file
   ```

### Configuration Examples

**Local Development**:
```env
ENVIRONMENT=local
DEBUG=true
LOG_LEVEL=DEBUG
```

**Remote Production**:
```env
ENVIRONMENT=remote
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_CREDENTIALS=false
```

### Code Structure Conventions
- Backend follows FastAPI patterns with dependency injection
- Frontend uses React functional components with hooks
- Shared TypeScript interfaces between frontend/backend
- Modular component architecture with clear separation of concerns

### MCP Tools Integration
The project includes comprehensive MCP (Model Context Protocol) tools integration:
- **GitHub API Tools**: 34+ tools for repository management, issues, PRs, releases
- **Web Scraping Tools**: Content extraction, URL fetching, data processing
- **File Operation Tools**: Advanced file manipulation and processing
- **Cache Management**: Performance optimization through intelligent caching

Access MCP tools through the API endpoints or direct service integration in `app/core/mcp_tools_service.py`

### Docker Support
The project includes complete Docker containerization with separated build and runtime optimization:
- **Multi-stage Dockerfile**: Three-stage build (frontend build -> backend build -> runtime)
- **Build optimization**: No resource constraints during build for reliability
- **Runtime optimization**: Python 3.12-slim base image with virtual environment execution
- **System dependencies**: curl, ca-certificates for minimal runtime requirements
- **docker-compose.yml**: Low resource consumption configuration (128MB RAM, 25% CPU limit)
- **Virtual environment**: Runtime uses `.venv/bin/python` directly without uv dependency
- **Production ready**: Optimized backend with `main_optimized.py` for minimal resource usage

#### Docker Build Variants
The project provides multiple Docker build options to handle different environments and dependency issues:

1. **Main Dockerfile (pnpm)** - Default build using pnpm
   ```bash
   make docker-build  # Uses pnpm with corepack
   ```

2. **Yarn Dockerfile** - Alternative for pnpm/corepack issues
   ```bash
   make docker-build-yarn  # Uses yarn instead of pnpm
   ```

3. **NPM Dockerfile** - Fallback for maximum compatibility
   ```bash
   make docker-build-npm  # Uses npm for broadest compatibility
   ```

#### Known Docker Issues & Solutions

**Issue**: pnpm/corepack activation failures in Docker build
- **Symptoms**: `corepack prepare pnpm@9.15.0 --activate` fails or times out
- **Root cause**: Network issues, corepack compatibility, or registry access problems
- **Solutions**:
  1. Use yarn alternative: `make docker-build-yarn`
  2. Use npm alternative: `make docker-build-npm`
  3. Add registry mirror to main Dockerfile: `pnpm config set registry https://registry.npmmirror.com`
  4. Increase Docker build timeout: `docker build --timeout 600`

**Issue**: Slow Docker builds with large Node.js images
- **Solutions**:
  1. Use Docker BuildKit cache: `DOCKER_BUILDKIT=1 docker build`
  2. Multi-stage builds already implemented for optimal layer caching
  3. Consider building in CI/CD with cached layers

#### Make Docker Targets
- **`docker-build`**: Main Docker build with pnpm
- **`docker-build-yarn`**: Alternative build using yarn
- **`docker-build-npm`**: Fallback build using npm
- **`docker-push`**: Push image to GHCR
- **`docker-up`**: Start containers with docker-compose
- **`docker-deploy`**: One-command build and deploy

### CI/CD Pipeline (Master Branch Only)
Automated Docker image building and publishing with GitHub Actions:
- **GitHub Actions workflow**: `.github/workflows/docker-build.yml`
- **Restricted triggers**: Only builds on push to master branch and version tags
- **Smart change detection**: Only builds when relevant files change (frontend/backend/docker/resources)
- **Advanced caching strategy**:
  - **pnpm store cache**: Global package store for faster dependency resolution
  - **Frontend build cache**: .next/cache for incremental compilation
  - **Backend dependency cache**: Python uv cache + .venv virtual environment
  - **Docker BuildKit cache**: Multi-level with mount cache for build layers
  - **Registry cache**: Docker images cached in GitHub Container Registry
- **Package management optimization**:
  - **pnpm**: ~40-70% faster than yarn/npm in CI environments
  - **Shamefully hoist**: Compatible with React Scripts ecosystem
  - **Content-addressable storage**: Eliminates duplicate downloads
- **Performance optimizations**: Latest BuildKit v0.12.4, disabled SBOM/Provenance for speed
- **Single-platform builds**: linux/amd64 optimized for reliability
- **Container registry**: Uses GitHub Container Registry (ghcr.io) for GitHub Packages
- **Tag-based builds**: Force builds on version tags regardless of file changes
- **Build skipping**: Intelligent skip notifications for documentation-only changes
- **Version management**: Automatic semantic versioning from git tags
- **Make targets**: `github-check`, `github-release` for CI/CD management

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.