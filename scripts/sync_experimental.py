#!/usr/bin/env python3

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import from parent directory
import requests
from result import Err, Ok, Result, is_err
from config import BuildConfig, VersionConfig


def main():
    """Main function to sync experimental versions."""
    print("Starting experimental version sync...")

    if not BuildConfig.is_experimental_enabled():
        print("Experimental builds are disabled. Skipping sync.")
        return

    result = sync_all_experimental_versions()

    if is_err(result):
        print(f"Error syncing experimental versions: {result.unwrap_err()}")
        exit(1)

    print("Experimental version sync completed successfully.")
    print(f"Summary: {result.unwrap()}")


def sync_all_experimental_versions() -> Result[str, str]:
    """Sync all available experimental versions."""
    try:
        # Get all available versions from PaperMC API
        versions_result = get_all_versions()
        if is_err(versions_result):
            return versions_result

        versions = versions_result.unwrap()
        synced_count = 0
        created_versions = []

        for version in versions:
            # Check if this version has experimental builds
            exp_build_result = get_latest_experimental_build(version)
            if is_err(exp_build_result):
                continue  # No experimental builds for this version

            exp_build = exp_build_result.unwrap()
            print(f"Found experimental build for version {version}: build {exp_build}")

            # Create or update version directory
            if create_experimental_version_directory(version, exp_build):
                synced_count += 1
                created_versions.append(f"{version}-exp{exp_build}")

        # Create/update experimental directory
        if created_versions:
            update_latest_experimental_directory()

        summary = f"Synced {synced_count} experimental versions: {', '.join(created_versions)}"
        return Ok(summary)

    except Exception as e:
        return Err(f"Unexpected error during sync: {e}")


def get_all_versions() -> Result[List[str], str]:
    """Get all available versions from PaperMC API."""
    try:
        response = requests.get("https://api.papermc.io/v2/projects/folia")
        response.raise_for_status()
        data = response.json()
        return Ok(data.get("versions", []))
    except Exception as e:
        return Err(f"Error fetching versions: {e}")


def get_latest_experimental_build(version: str) -> Result[int, str]:
    """Get the latest experimental build number for a version."""
    try:
        response = requests.get(f"https://api.papermc.io/v2/projects/folia/versions/{version}")
        response.raise_for_status()
        data = response.json()

        builds = data.get("builds", [])
        experimental_builds = []

        for build_info in builds:
            if isinstance(build_info, dict) and build_info.get("channel") == "experimental":
                experimental_builds.append(build_info["build"])

        if not experimental_builds:
            return Err(f"No experimental builds found for version {version}")

        # Return the highest build number
        return Ok(max(experimental_builds))

    except Exception as e:
        return Err(f"Error fetching experimental builds for {version}: {e}")


def create_experimental_version_directory(version: str, build: int) -> bool:
    """Create a version directory for experimental build."""
    try:
        versions_dir = Path(__file__).parent.parent / "versions"
        version_dir = versions_dir / version

        # Create directory if it doesn't exist
        if not version_dir.exists():
            print(f"Creating directory: {version_dir}")
            version_dir.mkdir(exist_ok=True)

            # Copy template files
            copy_template_files(version_dir, version, build, is_experimental=True)
            return True
        else:
            print(f"Directory already exists: {version_dir}")
            # Update existing directory if needed
            update_experimental_directory(version_dir, version, build)
            return False

    except Exception as e:
        print(f"Error creating experimental directory for {version}: {e}")
        return False


def copy_template_files(version_dir: Path, version: str, build: int, is_experimental: bool = False):
    """Copy template files to version directory."""
    # Get template from latest version
    template_dir = Path(__file__).parent.parent / "versions" / "latest"

    if not template_dir.exists():
        raise Exception("Template directory 'versions/latest' not found")

    # Files to copy
    files_to_copy = ["Dockerfile", "entrypoint.sh", "requirements.txt"]

    for file_name in files_to_copy:
        src_file = template_dir / file_name
        dst_file = version_dir / file_name

        if src_file.exists():
            shutil.copy2(src_file, dst_file)
            print(f"Copied {file_name} to {version_dir}")
        else:
            print(f"Warning: Template file {file_name} not found")

    # Create enhanced get-folia.py
    create_enhanced_get_folia(version_dir, version, build, is_experimental)

    # Create README.md
    create_version_readme(version_dir, version, build, is_experimental)


def create_enhanced_get_folia(version_dir: Path, version: str, build: int, is_experimental: bool):
    """Create enhanced get-folia.py for the version."""
    src_script = Path(__file__).parent.parent / "get-folia-enhanced.py"
    dst_script = version_dir / "get-folia.py"

    if not src_script.exists():
        raise Exception("Enhanced get-folia script not found")

    shutil.copy2(src_script, dst_script)

    # Make it executable
    os.chmod(dst_script, 0o755)


def create_version_readme(version_dir: Path, version: str, build: int, is_experimental: bool):
    """Create README.md for the version."""
    readme_content = f"""# Folia {version} {'(Experimental)' if is_experimental else ''}

This Docker image provides Folia Minecraft server version {version} {'build ' + str(build) + ' (experimental channel)' if is_experimental else ''}.

## Quick start

```bash
docker run -it -d -p 25565:25565 --name folia-{version} -e MINECRAFT_EULA=true ${DOCKER_NAMESPACE:-blackao}/folia:{version}{f'-exp{build}' if is_experimental else ''}
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
docker build --build-arg VERSION={version} --build-arg BUILD={build} -t ${DOCKER_NAMESPACE:-blackao}/folia:{version}{f'-exp{build}' if is_experimental else ''} .
```

## Experimental Build Information

{'This is an experimental build of Folia. Experimental builds may contain new features but can also have bugs. Use with caution in production environments.' if is_experimental else ''}

## License

This project is licensed under the terms of the GNU General Public License v3.0 License.
"""

    readme_file = version_dir / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)


def update_experimental_directory(version_dir: Path, version: str, build: int):
    """Update existing experimental directory with new build information."""
    print(f"Updating existing directory: {version_dir}")

    # Update get-folia.py if needed
    create_enhanced_get_folia(version_dir, version, build, is_experimental=True)

    # Update README.md
    create_version_readme(version_dir, version, build, is_experimental=True)


def update_latest_experimental_directory():
    """Create or update the experimental directory."""
    try:
        versions_dir = Path(__file__).parent.parent / "versions"
        latest_exp_dir = versions_dir / "experimental"

        # Find the most recent experimental version
        latest_version, latest_build = find_latest_experimental_version()

        if not latest_version:
            print("No experimental versions found to update experimental")
            return

        print(f"Updating experimental to point to {latest_version} build {latest_build}")

        # Remove existing directory if it exists
        if latest_exp_dir.exists():
            shutil.rmtree(latest_exp_dir)

        # Create new experimental directory
        latest_exp_dir.mkdir(exist_ok=True)
        copy_template_files(latest_exp_dir, latest_version, latest_build, is_experimental=True)

        # Create special README for experimental
        latest_readme = f"""# Latest Experimental Folia

This Docker image provides the latest experimental build of Folia Minecraft server.

**Current version:** {latest_version} build {latest_build}

## Quick start

```bash
docker run -it -d -p 25565:25565 --name folia-latest-exp -e MINECRAFT_EULA=true ${DOCKER_NAMESPACE:-blackao}/folia:experimental
```

## Experimental Build Warning

This is the latest experimental build of Folia. Experimental builds may contain new features but can also have bugs. Use with caution in production environments.

## Build Information

- **Version:** {latest_version}
- **Build:** {latest_build}
- **Channel:** experimental

## License

This project is licensed under the terms of the GNU General Public License v3.0 License.
"""

        readme_file = latest_exp_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(latest_readme)

    except Exception as e:
        print(f"Error updating experimental directory: {e}")


def find_latest_experimental_version() -> tuple[Optional[str], Optional[int]]:
    """Find the most recent experimental version."""
    try:
        versions_result = get_all_versions()
        if is_err(versions_result):
            return None, None

        versions = versions_result.unwrap()
        latest_version = None
        latest_build = None

        # Check versions in reverse order (newest first)
        for version in reversed(versions):
            build_result = get_latest_experimental_build(version)
            if not is_err(build_result):
                latest_version = version
                latest_build = build_result.unwrap()
                break

        return latest_version, latest_build

    except Exception as e:
        print(f"Error finding latest experimental version: {e}")
        return None, None


if __name__ == "__main__":
    main()