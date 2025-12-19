#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import DockerConfig


def main():
    """Push experimental Docker images to Docker Hub."""
    print("Pushing experimental Docker images...")

    # Known experimental versions with their proper tags
    experimental_versions = {
        "1.21.11": "1.21.11-exp2",  # version 1.21.11 build 2
        "latest-experimental": "latest-experimental"
    }

    for version_dir, image_tag in experimental_versions.items():
        if os.path.exists(f"versions/{version_dir}"):
            print(f"Pushing experimental version: {version_dir} as {image_tag}")
            push_experimental_image(image_tag)


def push_experimental_image(image_tag: str) -> bool:
    """Push a specific experimental Docker image to Docker Hub."""
    try:
        namespace = DockerConfig.get_namespace()
        image_name = f"{namespace}/folia:{image_tag}"

        cmd = f"docker push {image_name}"

        print(f"Pushing: {image_name}")
        result = os.system(cmd)

        if result == 0:
            print(f"✅ Successfully pushed: {image_name}")
            return True
        else:
            print(f"❌ Failed to push: {image_name}")
            return False

    except Exception as e:
        print(f"Error pushing experimental image {image_tag}: {e}")
        return False


if __name__ == "__main__":
    main()