#!/bin/bash

set -e

GITHUB_USERNAME="${1:-$(git config --get user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')}"

if [ -z "$GITHUB_USERNAME" ]; then
  echo "Error: Could not determine GitHub username"
  echo "Usage: $0 [github-username]"
  exit 1
fi

REGISTRY="ghcr.io/${GITHUB_USERNAME}"
SERVICES=("bot" "api" "frontend")
TAG="${2:-latest}"

case "${3:-pull}" in
  pull)
    echo "Pulling images from $REGISTRY with tag $TAG..."
    for service in "${SERVICES[@]}"; do
      image="$REGISTRY/aidialogs-$service:$TAG"
      echo "→ Pulling $image"
      docker pull "$image"
    done
    echo "✓ All images pulled successfully"
    ;;

  up)
    echo "Starting services with images from $REGISTRY ($TAG)..."
    export GITHUB_USERNAME="$GITHUB_USERNAME"
    docker-compose -f docker-compose.registry.yml up -d
    echo "✓ Services started"
    docker-compose -f docker-compose.registry.yml ps
    ;;

  down)
    echo "Stopping services..."
    docker-compose -f docker-compose.registry.yml down
    echo "✓ Services stopped"
    ;;

  logs)
    docker-compose -f docker-compose.registry.yml logs -f "${SERVICES[0]}" 2>/dev/null || true
    docker-compose -f docker-compose.registry.yml logs -f "${SERVICES[1]}" 2>/dev/null || true
    docker-compose -f docker-compose.registry.yml logs -f "${SERVICES[2]}" 2>/dev/null || true
    ;;

  *)
    echo "Usage: $0 [github-username] [tag] [command]"
    echo ""
    echo "Commands:"
    echo "  pull    Pull images from registry (default)"
    echo "  up      Start services with registry images"
    echo "  down    Stop services"
    echo "  logs    Show service logs"
    echo ""
    echo "Examples:"
    echo "  $0 myuser latest pull     # Pull latest images"
    echo "  $0 myuser latest up       # Start services"
    echo "  $0 myuser latest down     # Stop services"
    exit 1
    ;;
esac
