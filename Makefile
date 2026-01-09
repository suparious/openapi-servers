# OpenAPI Servers - Build and Push to Gitea Registry
#
# Usage:
#   make build-all          Build all server images
#   make push-all           Push all images to Gitea
#   make build-push-all     Build and push all images
#   make build-filesystem   Build single server
#   make push-filesystem    Push single server
#
# Configuration:
#   REGISTRY    Gitea registry URL (default: poseidon.hq.solidrust.net:30008)
#   OWNER       Registry owner (default: shaun)
#   TAG         Image tag (default: latest)

REGISTRY ?= poseidon.hq.solidrust.net:30008
OWNER ?= shaun
TAG ?= latest

# Servers deployed to Kubernetes
SERVERS := filesystem git memory weather

# All available servers (for future use)
ALL_SERVERS := filesystem git memory weather time graphiti summarizer mcp-proxy

.PHONY: help build-all push-all build-push-all login clean
.PHONY: $(addprefix build-,$(SERVERS)) $(addprefix push-,$(SERVERS))

help:
	@echo "OpenAPI Servers - Gitea Registry Management"
	@echo ""
	@echo "Usage:"
	@echo "  make login            Login to Gitea registry"
	@echo "  make build-all        Build all server images"
	@echo "  make push-all         Push all images to Gitea"
	@echo "  make build-push-all   Build and push all images"
	@echo ""
	@echo "Single server commands:"
	@echo "  make build-<server>   Build single server (e.g., make build-filesystem)"
	@echo "  make push-<server>    Push single server (e.g., make push-filesystem)"
	@echo ""
	@echo "Available servers: $(SERVERS)"
	@echo ""
	@echo "Configuration:"
	@echo "  REGISTRY=$(REGISTRY)"
	@echo "  OWNER=$(OWNER)"
	@echo "  TAG=$(TAG)"
	@echo ""
	@echo "Example with custom tag:"
	@echo "  make build-push-all TAG=v1.0.0"

login:
	@echo "Logging in to Gitea registry..."
	@echo "Note: Use your Gitea token as the password"
	docker login $(REGISTRY)

# Build targets
build-all: $(addprefix build-,$(SERVERS))
	@echo "✅ All images built"

build-filesystem:
	@echo "Building filesystem server..."
	docker build -t $(REGISTRY)/$(OWNER)/openapi-filesystem:$(TAG) servers/filesystem/

build-git:
	@echo "Building git server..."
	docker build -t $(REGISTRY)/$(OWNER)/openapi-git:$(TAG) servers/git/

build-memory:
	@echo "Building memory server..."
	docker build -t $(REGISTRY)/$(OWNER)/openapi-memory:$(TAG) servers/memory/

build-weather:
	@echo "Building weather server..."
	docker build -t $(REGISTRY)/$(OWNER)/openapi-weather:$(TAG) servers/weather/

# Push targets
push-all: $(addprefix push-,$(SERVERS))
	@echo "✅ All images pushed to $(REGISTRY)"

push-filesystem:
	@echo "Pushing filesystem server..."
	docker push $(REGISTRY)/$(OWNER)/openapi-filesystem:$(TAG)

push-git:
	@echo "Pushing git server..."
	docker push $(REGISTRY)/$(OWNER)/openapi-git:$(TAG)

push-memory:
	@echo "Pushing memory server..."
	docker push $(REGISTRY)/$(OWNER)/openapi-memory:$(TAG)

push-weather:
	@echo "Pushing weather server..."
	docker push $(REGISTRY)/$(OWNER)/openapi-weather:$(TAG)

# Combined build and push
build-push-all: build-all push-all
	@echo "✅ All images built and pushed"

# Clean local images
clean:
	@echo "Removing local openapi images..."
	-docker rmi $(REGISTRY)/$(OWNER)/openapi-filesystem:$(TAG) 2>/dev/null
	-docker rmi $(REGISTRY)/$(OWNER)/openapi-git:$(TAG) 2>/dev/null
	-docker rmi $(REGISTRY)/$(OWNER)/openapi-memory:$(TAG) 2>/dev/null
	-docker rmi $(REGISTRY)/$(OWNER)/openapi-weather:$(TAG) 2>/dev/null
	@echo "✅ Clean complete"

# Show current image status
status:
	@echo "Local images:"
	@docker images | grep -E "$(REGISTRY)/$(OWNER)/openapi" || echo "  No local openapi images found"
	@echo ""
	@echo "Registry: $(REGISTRY)"
	@echo "To check registry, use: curl -sk https://$(REGISTRY)/v2/_catalog"
