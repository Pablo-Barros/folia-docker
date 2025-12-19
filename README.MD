# Folia - All Versions

This Docker image provides Folia Minecraft server versions. You can easily run a Minecraft server using this image.

## Quick start

```bash
docker run -it -d -p 25565:25565 --name endkind-folia -e MINECRAFT_EULA=true ${DOCKER_NAMESPACE:-endkind}/folia:latest
```

This command starts a Folia server in detached mode (-d), maps port 25565 from the host to the container, and accepts the Minecraft EULA.

## Installation and Configuration (Recommended)

```bash
docker volume create endkind-folia

docker run -it -d -p 25565:25565 --name endkind-folia -v endkind-folia:/folia -e MAX_RAM=3G -e MINECRAFT_EULA=true --restart=always ${DOCKER_NAMESPACE:-endkind}/folia:latest
```

## Configuration

### Docker Namespace

This fork supports configurable Docker namespaces. Set the `DOCKER_NAMESPACE` environment variable to use your own Docker Hub username:

```bash
export DOCKER_NAMESPACE=yourusername
docker run -it -d -p 25565:25565 -e MINECRAFT_EULA=true $DOCKER_NAMESPACE/folia:latest
```

Or create a `.env` file:

```bash
echo "DOCKER_NAMESPACE=yourusername" > .env
```

### Experimental Builds

This repository includes support for experimental/unstable Folia builds. Experimental builds are tagged with the `-exp` suffix:

```bash
# Example: Run experimental Folia 1.21.11 build #2
docker run -it -d -p 25565:25565 -e MINECRAFT_EULA=true ${DOCKER_NAMESPACE:-endkind}/folia:1.21.11-exp2
```

**⚠️ Warning:** Experimental builds may contain new features but can also have bugs. Use with caution in production environments.

## Using Specific Versions

When deploying your server for production or if you require version stability, consider using specific image versions. For example:

### Folia 1.19.4 (Stable)

```bash
docker run -it -d -p 25565:25565 -e MINECRAFT_EULA=true ${DOCKER_NAMESPACE:-endkind}/folia:1.19.4
```

By specifying a version like 1.19.4, you ensure that your server runs a known and tested version of Folia.

### All Supported Versions

#### Stable Versions
- `latest` uses always the newest stable version
- `1.21.4`, `1.21.5`, `1.21.6`, `1.21.8`
- `1.20.1`, `1.20.2`, `1.20.4`, `1.20.6`
- `1.19.4`

#### Experimental Versions
- `latest-experimental` points to the latest experimental build
- `1.21.11-exp2` (experimental build #2)
- Experimental versions use the `{version}-exp{build}` naming convention

## Environment variables

You can customize your Folia server by setting the following environment variables:

- `MIN_RAM` (default: 512M) - Minimum RAM allocated for the server.
- `MAX_RAM` (default: 1G) - Maximum RAM allocated for the server.
- `MINECRAFT_EULA` (default: false) - Set to `true` to accept the Minecraft EULA.
- `JAVA_FLAGS` - Additional Java flags generated with [flags.sh](https://flags.sh/).
- `FOLIA_FLAGS` (default: --nojline) - Custom Folia server flags.
- `TZ` (example: Europe/Berlin) - Set the time zone for the server.

These environment variables allow you to tailor your Folia server's configuration to your specific requirements. You can adjust memory allocation, specify custom Java flags, and configure various server settings to suit your needs.

## How to build

### Stable Versions

Replace `<version>` with the desired version.

```bash
export DOCKER_NAMESPACE=yourusername
docker build --build-arg FOLIA_VERSION=<version> -t $DOCKER_NAMESPACE/folia:<version> ./versions/<version>
```

### Experimental Versions

For experimental builds, specify the version and build:

```bash
export DOCKER_NAMESPACE=yourusername
docker build --build-arg VERSION=1.21.11 --build-arg BUILD=2 -t $DOCKER_NAMESPACE/folia:1.21.11-exp2 ./versions/1.21.11
```

### Build All Versions

Use the provided build script to build all versions:

```bash
export DOCKER_NAMESPACE=yourusername
python build.py
```

## Additional Information

- [GitHub Repository](https://github.com/Endkind/folia)
- [Docker Repository](https://hub.docker.com/r/endkind/folia)
- [Docker Compose Example](https://github.com/Endkind/folia/blob/main/docker-compose.yml)
- [Visit our website](https://www.endkind.net) for more information about our projects and services.
- Connect to our Minecraft server (crossplay) at `mc.endkind.net` and start your adventure!

## License

This project is licensed under the terms of the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/) License.

### Other License

This project includes code derived from the [Folia](https://github.com/PaperMC/folia) project.
