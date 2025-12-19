# Folia 1.21.11 (Experimental)

This Docker image provides Folia Minecraft server version 1.21.11 build 2 (experimental channel).

## Quick start

```bash
docker run -it -d -p 25565:25565 --name folia-1.21.11 -e MINECRAFT_EULA=true ${DOCKER_NAMESPACE:-endkind}/folia:1.21.11-exp2
```

## Environment variables

- `MIN_RAM` (default: 512M) - Minimum RAM allocated for the server
- `MAX_RAM` (default: 1G) - Maximum RAM allocated for the server
- `MINECRAFT_EULA` (default: false) - Set to `true` to accept the Minecraft EULA
- `JAVA_FLAGS` - Additional Java flags
- `FOLIA_FLAGS` (default: --nojline) - Custom Folia server flags
- `TZ` (example: Europe/Berlin) - Set the time zone for the server

## Build from source

```bash
docker build --build-arg VERSION=1.21.11 --build-arg BUILD=2 -t ${DOCKER_NAMESPACE:-endkind}/folia:1.21.11-exp2 .
```

## Experimental Build Information

This is an experimental build of Folia. Experimental builds may contain new features but can also have bugs. Use with caution in production environments.

**Build Details:**
- Version: 1.21.11
- Build: 2
- Channel: experimental
- Downloaded from: PaperMC API

## License

This project is licensed under the terms of the GNU General Public License v3.0 License.