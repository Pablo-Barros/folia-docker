# Folia 1.21.4 (Experimental)

This Docker image provides Folia Minecraft server version 1.21.4 (experimental build).

**Build:** latest
**Channel:** experimental

## Quick start

```bash
docker run -it -d -p 25565:25565 --name folia-1.21.4 -e MINECRAFT_EULA=true blackao/folia:1.21.4
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
docker build --build-arg VERSION=1.21.4 --build-arg BUILD=latest -t blackao/folia:1.21.4 versions/1.21.4/
```

## Experimental Build Warning

This is an experimental build of Folia. Experimental builds may contain new features but can also have bugs. Use with caution in production environments.

## License

This project is licensed under the terms of the GNU General Public License v3.0 License.
