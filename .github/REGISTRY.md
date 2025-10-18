# GitHub Container Registry Setup

## Overview

This project publishes Docker images to GitHub Container Registry (ghcr.io) through GitHub Actions workflow.

## Published Images

- `ghcr.io/<owner>/aidialogs-bot`
- `ghcr.io/<owner>/aidialogs-api`
- `ghcr.io/<owner>/aidialogs-frontend`

Where `<owner>` is the repository owner (username or organization).

## Making Images Public

By default, images published to GHCR are private. To make them publicly accessible:

### Option 1: GitHub UI (Manual)
1. Go to your GitHub profile → Packages
2. Click on the image package (e.g., `aidialogs-bot`)
3. Package settings → Manage repository access
4. Change visibility to **Public**
5. Repeat for each image (bot, api, frontend)

### Option 2: GitHub CLI
```bash
gh api repos/<owner>/aidialogs/package-settings \
  -X PATCH \
  -f visibility=public
```

## Accessing Public Images

Once images are public, anyone can pull them without authentication:

```bash
# Pull latest version
docker pull ghcr.io/<owner>/aidialogs-bot:latest
docker pull ghcr.io/<owner>/aidialogs-api:latest
docker pull ghcr.io/<owner>/aidialogs-frontend:latest

# Pull specific version
docker pull ghcr.io/<owner>/aidialogs-bot:v1.0.0
```

## Workflow Automation

The `.github/workflows/build.yml` workflow:
- Triggers on `push` to main/develop and on release tags
- Builds images for all 3 services in parallel (matrix strategy)
- Pushes to GHCR automatically
- Uses GitHub Actions cache for layer caching

See `docs/github-actions-guide.md` for detailed workflow documentation.
