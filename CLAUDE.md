# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-version Docker image project for Folia Minecraft server. The repository contains separate Docker build contexts for each supported Minecraft version, automated build/push scripts, and CI/CD workflows.

## Architecture

- **Root level**: Contains Python build automation scripts (`build.py`, `push.py`, `utils.py`)
- **`versions/` directory**: Each subdirectory represents a Minecraft version with its own Docker build context
- **Version directories**: Contain version-specific `Dockerfile`, `get-folia.py`, and `entrypoint.sh`
- **CI/CD**: GitHub Actions workflows for automated releases and dependency updates

### Key Components

- **`get-folia.py`**: Downloads Folia JAR files from PaperMC API for specific versions/builds
- **`build.py`**: Builds Docker images for all or specific discovered versions
- **`push.py`**: Pushes built images to Docker Hub
- **`utils.py`**: Version discovery and sorting utilities
- **Multi-stage Dockerfiles**: Python build stage + Java runtime stage

## Development Commands

### Setup Environment
```bash
# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Build Commands
```bash
# Build all versions
python build.py

# Build specific versions
python build.py 1.21.8 latest

# Build single version manually
docker build --build-arg FOLIA_VERSION=1.21.8 -t endkind/folia:1.21.8 ./versions/1.21.8
```

### Push Commands
```bash
# Push all versions
python push.py

# Push specific versions (modify push.py script to accept arguments like build.py)
```

### Testing
```bash
# Test container locally
docker run -it -p 25565:25565 -e MINECRAFT_EULA=true endkind/folia:latest

# With Docker Compose
docker-compose up -d
```

## Version Management

- **Version discovery**: `utils.py` automatically discovers versions from `versions/` directory
- **Version sorting**: Supports semantic versioning with pre-release identifiers
- **Disabling versions**: Create `.disabled` file in version directory to exclude from builds
- **Latest version**: Always points to newest Folia release with available build

## File Structure Pattern

Each version directory contains:
- `Dockerfile`: Multi-stage build with version-specific arguments
- `get-folia.py`: Identical download script with version-specific defaults
- `entrypoint.sh`: Server startup script with restart loop
- `README.md`: Version-specific documentation

## CI/CD Workflows

- **Release workflow**: Triggers on releases, schedule (Mondays 3AM UTC), or manual dispatch
- **Check update workflow**: Monitors for new Folia releases
- **Release drafter**: Automatic changelog generation

## Environment Variables

- `MIN_RAM`: Default 512M - Minimum JVM memory
- `MAX_RAM`: Default 1G - Maximum JVM memory
- `JAVA_FLAGS`: Additional JVM arguments
- `FOLIA_FLAGS`: Default "--nojline" - Server startup flags
- `MINECRAFT_EULA`: Must be set to "true" to accept Minecraft EULA
- `VERSION`: Folia version (for get-folia.py)
- `BUILD`: Specific build number (defaults to "latest")