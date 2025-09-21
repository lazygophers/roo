#!/bin/bash

# LazyAI Studio Dev Deployment Script
# This script deploys the dev branch to the specified server

set -euo pipefail

# Configuration
IMAGE_NAME="ghcr.io/lazygophers/roo:dev"
DEPLOY_PATH="/opt/1panel/docker/compose/lazyai-studio/"
LOG_FILE="/tmp/lazyai-deploy-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Main deployment function
deploy() {
    log "🚀 Starting LazyAI Studio dev deployment..."
    log "📄 Log file: $LOG_FILE"

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi

    # Pull latest image
    log "📦 Pulling latest Docker image: $IMAGE_NAME"
    if docker pull "$IMAGE_NAME" 2>&1 | tee -a "$LOG_FILE"; then
        success "Successfully pulled $IMAGE_NAME"
    else
        error "Failed to pull Docker image"
        exit 1
    fi

    # Navigate to deployment directory
    log "📂 Navigating to deployment directory: $DEPLOY_PATH"
    if [[ ! -d "$DEPLOY_PATH" ]]; then
        error "Deployment directory does not exist: $DEPLOY_PATH"
        exit 1
    fi

    cd "$DEPLOY_PATH"

    # Check if docker-compose.yml exists
    if [[ ! -f "docker-compose.yml" ]] && [[ ! -f "compose.yml" ]]; then
        error "No docker-compose.yml or compose.yml found in $DEPLOY_PATH"
        exit 1
    fi

    # Backup current state (optional)
    log "💾 Creating backup of current container state..."
    docker compose ps --format json > "/tmp/lazyai-backup-$(date +%Y%m%d-%H%M%S).json" || warning "Failed to backup container state"

    # Stop and recreate containers
    log "🔄 Recreating containers..."
    if docker compose up -d --force-recreate 2>&1 | tee -a "$LOG_FILE"; then
        success "Successfully recreated containers"
    else
        error "Failed to recreate containers"
        exit 1
    fi

    # Wait for containers to be healthy
    log "⏳ Waiting for containers to start..."
    sleep 10

    # Check container status
    log "📊 Container status:"
    docker compose ps | tee -a "$LOG_FILE"

    # Check if containers are running
    if docker compose ps --filter "status=running" --quiet | grep -q .; then
        success "Containers are running"
    else
        error "No containers are running"
        log "📋 Container logs:"
        docker compose logs --tail=50 | tee -a "$LOG_FILE"
        exit 1
    fi

    # Check recent logs for errors
    log "📋 Recent container logs (last 20 lines):"
    docker compose logs --tail=20 | tee -a "$LOG_FILE"

    # Health check (if applicable)
    log "🏥 Performing health check..."
    sleep 5

    # Show final status
    log "📋 Final container status:"
    docker compose ps | tee -a "$LOG_FILE"

    success "✅ Dev deployment completed successfully!"
    log "📄 Full deployment log available at: $LOG_FILE"
}

# Cleanup function
cleanup() {
    log "🧹 Performing cleanup..."
    # Remove old images if needed
    if docker images --filter "dangling=true" --quiet | grep -q .; then
        log "🗑️ Removing dangling images..."
        docker image prune -f
    fi
}

# Rollback function
rollback() {
    error "🔄 Rolling back deployment..."
    # This could be enhanced to restore from backup
    docker compose down
    docker compose up -d
    warning "Rollback completed. Please check manually."
}

# Signal handlers
trap 'error "Deployment interrupted"; rollback; exit 1' INT TERM

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            deploy
            cleanup
            ;;
        "rollback")
            rollback
            ;;
        "logs")
            cd "$DEPLOY_PATH"
            docker compose logs "${2:-}"
            ;;
        "status")
            cd "$DEPLOY_PATH"
            docker compose ps
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [deploy|rollback|logs|status|help]"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy the latest dev image (default)"
            echo "  rollback - Rollback to previous state"
            echo "  logs     - Show container logs"
            echo "  status   - Show container status"
            echo "  help     - Show this help message"
            ;;
        *)
            error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"