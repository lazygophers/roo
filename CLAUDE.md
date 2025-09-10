# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LazyAI Studio** - LazyGophers 组织出品的 AI 智能工作室。这是一个专为懒人开发者设计的综合性 AI 开发解决方案，通过智能模式、个性角色和便捷命令，让复杂的开发工作变得简单高效。

项目核心是一个强大的配置管理系统，能够处理基于 YAML 的 AI 模式定义，并与 VS Code 扩展无缝集成，为开发者提供完整的 AI 辅助开发体验。

## Commands

### Development & Testing
```bash
# Install all dependencies
make install

# Start development server (with integrated frontend)
make backend-dev

# Start production server
make run

# Build frontend for production
make build

# Run tests
make test

# Generate custom_models.yaml from resources/models/*.yaml
uv run python merge.py

# Clean build files
make clean
```

## Architecture

### Core Components

1. **Mode Processing System** (`merge.py`)
   - Reads model definitions from `resources/models/*.yaml`
   - Injects hooks from `resources/hooks/before.md` and `resources/hooks/after.md`
   - Generates consolidated `custom_models.yaml` for VS Code extensions
   - Ensures `orchestrator` mode is always first in output

2. **Model Structure**
   - Each mode defined in separate YAML under `resources/models/`
   - Required fields: slug, name, roleDefinition, customInstructions, whenToUse, description, groups
   - Modes include specialized variants for languages (code-python, code-golang, etc.)

3. **Rules System** (`resources/rules*/`)
   - Language-specific rules directories (rules-code-python, rules-code-golang, etc.)
   - Core rules in `resources/rules/` including memory management, task delegation, mode selection
   - Rules are copied to `~/.roo/` and `~/.kilocode/` during deployment

4. **Deployment** (`update.sh`)
   - Copies generated `custom_models.yaml` to VS Code extension directories:
     - `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/`
     - `~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-code-nightly/`
     - `~/Library/Application Support/Code/User/globalStorage/kilocode.kilo-code/`
   - Deploys rules and commands to `~/.roo/` and `~/.kilocode/` directories
   - Copies role files (bunny_maid.md) to rules directories

### Key Modes

- **orchestrator** (Brain): Task decomposition and model selection hub
- **architect**: System design and technical architecture  
- **code/code-***: Language-specific implementation modes
- **debug**: Systematic bug tracking and resolution
- **doc-writer**: Technical documentation creation
- **project-research**: Codebase analysis and insights
- **memory**: Deterministic memory management workflows

## Development Guidelines

### Mode Development
- Edit mode definitions in `resources/models/*.yaml`
- Run `uv run python merge.py` to regenerate `custom_models.yaml`
- Use `./update.sh` to deploy changes locally

### Testing
- Tests directory doesn't exist yet - create `tests/` for Python tests
- Use `uv run pytest tests/ -v` for Python testing
- Test dependencies already included in `pyproject.toml` (pytest, pytest-asyncio, pytest-cov, httpx)

### Technology Stack
- **Python**: 3.12+ with UV package manager
- **Core Dependencies**: FastAPI, Flask, PyYAML, Rich, TinyDB, Uvicorn
- **Development**: Virtual environment in `.venv/`, dependencies in `pyproject.toml`
- **Backend Structure**: Minimal FastAPI app structure in `app/` (core, models, routers)