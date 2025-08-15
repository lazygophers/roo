# ========================================
# Docker Build Management for MCP stdio Service
# Project: lazygopher (MCP Memory Suite)
# ========================================

# Configuration Variables
# ----------------------------------------
PROJECT_NAME := lazygopher
IMAGE_NAME := $(PROJECT_NAME)
REGISTRY ?= 
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
BUILD_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Docker Configuration
DOCKERFILE := Dockerfile
DOCKER_CONTEXT := .
BUILD_ARGS := --build-arg VERSION=$(VERSION) \
              --build-arg BUILD_DATE=$(BUILD_DATE) \
              --build-arg GIT_COMMIT=$(GIT_COMMIT) \
			  --debug=true

# Image Tags
IMAGE_TAG := $(IMAGE_NAME):$(VERSION)
IMAGE_LATEST := $(IMAGE_NAME):latest
FULL_IMAGE_TAG := $(if $(REGISTRY),$(REGISTRY)/$(IMAGE_TAG),$(IMAGE_TAG))
FULL_IMAGE_LATEST := $(if $(REGISTRY),$(REGISTRY)/$(IMAGE_LATEST),$(IMAGE_LATEST))

# Container Configuration
CONTAINER_NAME := $(PROJECT_NAME)_mcp
ENV_FILE ?= .env
VOLUME_MOUNT ?= $(PWD)/data:/app/data

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# ========================================
# Build Commands
# ========================================

.PHONY: build
build: ## Build Docker image with current version tag
	@echo "$(BLUE)Building Docker image: $(IMAGE_TAG)$(NC)"
	@docker build $(BUILD_ARGS) \
		-t $(IMAGE_TAG) \
		-f $(DOCKERFILE) \
		$(DOCKER_CONTEXT)
	@echo "$(GREEN)✓ Image built successfully: $(IMAGE_TAG)$(NC)"

.PHONY: build-latest
build-latest: build ## Build Docker image with latest tag
	@echo "$(BLUE)Tagging image as latest$(NC)"
	@docker tag $(IMAGE_TAG) $(IMAGE_LATEST)
	@echo "$(GREEN)✓ Tagged as: $(IMAGE_LATEST)$(NC)"

.PHONY: build-dev
build-dev: ## Build Docker image for development (with cache mount)
	@echo "$(BLUE)Building development image with cache$(NC)"
	@docker build $(BUILD_ARGS) \
		--target builder \
		-t $(IMAGE_NAME):dev \
		-f $(DOCKERFILE) \
		$(DOCKER_CONTEXT)
	@echo "$(GREEN)✓ Development image built$(NC)"

.PHONY: build-no-cache
build-no-cache: ## Build Docker image without cache
	@echo "$(YELLOW)Building without cache (this may take longer)$(NC)"
	@docker build --no-cache $(BUILD_ARGS) \
		-t $(IMAGE_TAG) \
		-f $(DOCKERFILE) \
		$(DOCKER_CONTEXT)
	@echo "$(GREEN)✓ Image built without cache$(NC)"

.PHONY: build-multi
build-multi: ## Build multi-platform image (amd64, arm64)
	@echo "$(BLUE)Building multi-platform image$(NC)"
	@docker buildx build \
		--platform linux/amd64,linux/arm64 \
		$(BUILD_ARGS) \
		-t $(IMAGE_TAG) \
		-f $(DOCKERFILE) \
		$(DOCKER_CONTEXT)
	@echo "$(GREEN)✓ Multi-platform image built$(NC)"

# ========================================
# Run Commands (stdio MCP Service)
# ========================================

.PHONY: run
run: ## Run MCP service interactively (stdio mode)
	@echo "$(CYAN)Starting MCP stdio service$(NC)"
	@echo "$(YELLOW)This is an interactive stdio service - communicate via stdin/stdout$(NC)"
	@docker run --rm -i \
		--name $(CONTAINER_NAME) \
		-v $(VOLUME_MOUNT) \
		$(if $(wildcard $(ENV_FILE)),--env-file $(ENV_FILE),) \
		$(IMAGE_TAG)

.PHONY: run-dev
run-dev: ## Run development container with live reload
	@echo "$(CYAN)Running development MCP service$(NC)"
	@docker run --rm -it \
		--name $(CONTAINER_NAME)_dev \
		-v $(PWD):/app \
		-v /app/.venv \
		$(if $(wildcard $(ENV_FILE)),--env-file $(ENV_FILE),) \
		-e DEV_MODE=true \
		$(IMAGE_NAME):dev

.PHONY: run-shell
run-shell: ## Run container with shell access for debugging
	@echo "$(BLUE)Starting shell in container$(NC)"
	@docker run --rm -it \
		--name $(CONTAINER_NAME)_shell \
		-v $(VOLUME_MOUNT) \
		$(if $(wildcard $(ENV_FILE)),--env-file $(ENV_FILE),) \
		--entrypoint /bin/bash \
		$(IMAGE_TAG)

.PHONY: test-mcp
test-mcp: ## Test MCP service with sample input
	@echo "$(PURPLE)Testing MCP service with sample request$(NC)"
	@echo '{"jsonrpc": "2.0", "method": "get_timestamp", "id": 1}' | \
		docker run --rm -i \
		-v $(VOLUME_MOUNT) \
		$(if $(wildcard $(ENV_FILE)),--env-file $(ENV_FILE),) \
		$(IMAGE_TAG)

# ========================================
# Container Management
# ========================================

.PHONY: logs
logs: ## Show logs from recent container runs
	@echo "$(BLUE)Showing recent Docker logs for $(IMAGE_NAME)$(NC)"
	@docker logs $(shell docker ps -a -q --filter ancestor=$(IMAGE_TAG) | head -1) 2>/dev/null || \
		echo "$(YELLOW)No recent container logs found$(NC)"

.PHONY: ps
ps: ## Show running containers for this project
	@echo "$(BLUE)Active containers for $(PROJECT_NAME):$(NC)"
	@docker ps --filter name=$(PROJECT_NAME) --format "table {{.Names}}\t{{.Status}}\t{{.Command}}"

.PHONY: inspect
inspect: ## Inspect the Docker image
	@echo "$(BLUE)Image details for $(IMAGE_TAG):$(NC)"
	@docker inspect $(IMAGE_TAG) | jq '.[0] | {Id: .Id, Created: .Created, Size: .Size, Architecture: .Architecture, Os: .Os}'

# ========================================
# Cleanup Commands
# ========================================

.PHONY: clean
clean: ## Remove all containers and images for this project
	@echo "$(YELLOW)Cleaning up containers and images$(NC)"
	@docker rm -f $(shell docker ps -a -q --filter name=$(PROJECT_NAME)) 2>/dev/null || true
	@docker rmi $(IMAGE_TAG) $(IMAGE_LATEST) $(IMAGE_NAME):dev 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: clean-all
clean-all: clean ## Remove all project images including intermediate layers
	@echo "$(YELLOW)Removing all related images$(NC)"
	@docker images -q $(IMAGE_NAME)* | xargs -r docker rmi -f 2>/dev/null || true
	@echo "$(GREEN)✓ All images removed$(NC)"

.PHONY: prune
prune: ## Prune unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources$(NC)"
	@docker system prune -f
	@echo "$(GREEN)✓ System pruned$(NC)"

# ========================================
# Registry Commands
# ========================================

.PHONY: push
push: ## Push image to registry
	@if [ -z "$(REGISTRY)" ]; then \
		echo "$(RED)Error: REGISTRY is not set$(NC)"; \
		echo "Usage: make push REGISTRY=your-registry.com"; \
		exit 1; \
	fi
	@echo "$(BLUE)Pushing $(FULL_IMAGE_TAG) to registry$(NC)"
	@docker tag $(IMAGE_TAG) $(FULL_IMAGE_TAG)
	@docker push $(FULL_IMAGE_TAG)
	@echo "$(GREEN)✓ Image pushed: $(FULL_IMAGE_TAG)$(NC)"

.PHONY: push-latest
push-latest: push ## Push image with latest tag
	@echo "$(BLUE)Pushing $(FULL_IMAGE_LATEST) to registry$(NC)"
	@docker tag $(IMAGE_TAG) $(FULL_IMAGE_LATEST)
	@docker push $(FULL_IMAGE_LATEST)
	@echo "$(GREEN)✓ Latest image pushed: $(FULL_IMAGE_LATEST)$(NC)"

.PHONY: pull
pull: ## Pull image from registry
	@if [ -z "$(REGISTRY)" ]; then \
		echo "$(RED)Error: REGISTRY is not set$(NC)"; \
		echo "Usage: make pull REGISTRY=your-registry.com"; \
		exit 1; \
	fi
	@echo "$(BLUE)Pulling $(FULL_IMAGE_TAG) from registry$(NC)"
	@docker pull $(FULL_IMAGE_TAG)
	@docker tag $(FULL_IMAGE_TAG) $(IMAGE_TAG)
	@echo "$(GREEN)✓ Image pulled: $(IMAGE_TAG)$(NC)"

# ========================================
# Utility Commands
# ========================================

.PHONY: version
version: ## Show current version
	@echo "$(CYAN)Project Version Information:$(NC)"
	@echo "  Version:    $(VERSION)"
	@echo "  Git Commit: $(GIT_COMMIT)"
	@echo "  Build Date: $(BUILD_DATE)"
	@echo "  Image Tag:  $(IMAGE_TAG)"

.PHONY: size
size: ## Show image size
	@echo "$(BLUE)Image sizes:$(NC)"
	@docker images $(IMAGE_NAME) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

.PHONY: test
test: ## Run tests inside container
	@echo "$(PURPLE)Running tests in container$(NC)"
	@docker run --rm \
		-v $(VOLUME_MOUNT) \
		$(if $(wildcard $(ENV_FILE)),--env-file $(ENV_FILE),) \
		--entrypoint pytest \
		$(IMAGE_TAG) \
		tests/ -v

.PHONY: lint
lint: ## Run linters inside container
	@echo "$(PURPLE)Running linters$(NC)"
	@docker run --rm \
		-v $(PWD):/app \
		--entrypoint /bin/bash \
		$(IMAGE_TAG) \
		-c "ruff check . && mypy src/"

.PHONY: format
format: ## Format code inside container
	@echo "$(PURPLE)Formatting code$(NC)"
	@docker run --rm \
		-v $(PWD):/app \
		--entrypoint /bin/bash \
		$(IMAGE_TAG) \
		-c "ruff format . && ruff check --fix ."

# ========================================
# Development Helpers
# ========================================

.PHONY: dev-setup
dev-setup: ## Setup development environment
	@echo "$(CYAN)Setting up development environment$(NC)"
	@cp .env.example .env 2>/dev/null || echo "$(YELLOW).env file already exists$(NC)"
	@mkdir -p data 2>/dev/null || true
	@echo "$(GREEN)✓ Development environment ready$(NC)"

.PHONY: validate
validate: ## Validate Dockerfile and configuration
	@echo "$(BLUE)Validating configuration$(NC)"
	@docker build --check $(DOCKERFILE) 2>/dev/null || docker build --no-cache --target builder -f $(DOCKERFILE) . > /dev/null
	@echo "$(GREEN)✓ Dockerfile is valid$(NC)"
	@if [ -f docker-compose.yml ]; then \
		docker-compose config > /dev/null && echo "$(GREEN)✓ docker-compose.yml is valid$(NC)"; \
	fi

# ========================================
# Help Command
# ========================================

.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)========================================$(NC)"
	@echo "$(CYAN)     MCP Docker Build Management$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make <target> [VARIABLE=value ...]"
	@echo ""
	@echo "$(YELLOW)Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-18s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Variables:$(NC)"
	@echo "  $(CYAN)VERSION$(NC)          Docker image version (default: git tag or 'dev')"
	@echo "  $(CYAN)REGISTRY$(NC)         Docker registry URL for push/pull"
	@echo "  $(CYAN)ENV_FILE$(NC)         Environment file path (default: .env)"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make build                     # Build Docker image"
	@echo "  make run                        # Run MCP service interactively"
	@echo "  make test-mcp                   # Test MCP service"
	@echo "  make push REGISTRY=myregistry  # Push to registry"
	@echo ""
	@echo "$(GREEN)Note: This is a stdio-based MCP service$(NC)"
	@echo "$(GREEN)It communicates via stdin/stdout, not network ports$(NC)"

.PHONY: all
all: clean build test ## Clean, build, and test

# Set help as default goal if no target specified
.DEFAULT: help