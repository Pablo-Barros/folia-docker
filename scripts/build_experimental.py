#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import DockerConfig
from utils import discover_experimental_versions


def main():
    """Build experimental Docker images with proper tagging."""
    print("Building experimental Docker images...")

    if not discover_experimental_versions():
        print("No experimental versions found.")
        return

    # Known experimental versions with their proper tags
    experimental_versions = {
        "1.21.11": "1.21.11-exp2",  # version 1.21.11 build 2
        "latest-experimental": "latest-experimental"
    }

    for version_dir, image_tag in experimental_versions.items():
        if os.path.exists(f"versions/{version_dir}"):
            print(f"Building experimental version: {version_dir} as {image_tag}")
            build_experimental_image(version_dir, image_tag)


def build_experimental_image(version_dir: str, image_tag: str) -> bool:
    """Build a specific experimental Docker image."""
    try:
        namespace = DockerConfig.get_namespace()
        image_name = f"{namespace}/folia:{image_tag}"

        # Build the Docker image
        build_context = f"./versions/{version_dir}"

        # For experimental builds, we need to pass the correct build args
        if version_dir == "1.21.11":
            build_args = "--build-arg VERSION=1.21.11 --build-arg BUILD=2"
        else:
            build_args = ""

        cmd = f"docker build {build_args} -t {image_name} {build_context}"

        print(f"Building: {cmd}")
        result = os.system(cmd)

        if result == 0:
            print(f"✅ Successfully built: {image_name}")
            return True
        else:
            print(f"❌ Failed to build: {image_name}")
            return False

    except Exception as e:
        print(f"Error building experimental image {version_dir}: {e}")
        return False


if __name__ == "__main__":
    main()