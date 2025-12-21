import subprocess
import sys
from typing import List

from result import Err, Ok, Result, is_err, is_ok

from config import DockerConfig
from utils import discover_versions, get_latest_stable_or_experimental_build


def main():
    if len(sys.argv) > 1:
        versions = sys.argv[1:]
        result = push_all(versions)
    else:
        result = push_all()

    if is_ok(result):
        print(f"Push process succeeded: {result.unwrap()}")
    elif is_err(result):
        print(f"Push process failed: {result.unwrap_err()}")
        exit(1)


def push(tag: str) -> Result[str, str]:
    """
    Push a Docker image with the specified tag to Docker Hub.

    Args:
        tag: The tag of the image

    Returns:
        Result[str, str]: Ok with success message or Err with error message
    """
    try:
        # Handle experimental tagging with stable-first logic (mirror build.py logic)
        if tag == "experimental":
            # Experimental tag always points to 1.21.11 for now (can be made dynamic later)
            image_name = DockerConfig.get_image_name("experimental")
        elif tag == "1.21.11":
            # Use stable-first logic for version tags (mirror build.py logic)
            build_result = get_latest_stable_or_experimental_build("1.21.11")
            if not build_result or not build_result[0]:
                return Err("No builds available for version 1.21.11")

            build_number = build_result[0]
            is_experimental = build_result[1]

            if is_experimental:
                # Use experimental-specific tag
                image_name = f"{DockerConfig.get_namespace()}/folia:1.21.11-exp{build_number}"
            else:
                # Use standard version tag for stable builds
                image_name = DockerConfig.get_image_name("1.21.11")
        elif tag == "latest":
            image_name = DockerConfig.get_image_name("latest")
        else:
            image_name = DockerConfig.get_image_name(tag)

        cmd = ["docker", "push", image_name]

        print(f"Pushing Docker image: {image_name}")
        print(f"Command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        return Ok(f"Docker image '{image_name}' pushed successfully")

    except subprocess.CalledProcessError as e:
        error_msg = f"Docker push failed: {e.stderr if e.stderr else e.stdout}"
        return Err(error_msg)
    except Exception as e:
        return Err(f"Unexpected error: {str(e)}")


def push_all(versions: List[str] = discover_versions()) -> Result[str, str]:
    """
    Push Docker images based on successful builds from manifest.
    """
    if not versions:
        return Err("No build configurations found!")

    print(f"Found {len(versions)} build configurations:")
    for version in versions:
        print(f"- {version}")

    print("\nStarting pushes...\n")

    success_count = 0
    for version in versions:
        print(f"--- Pushing folia:{version} ---")
        result = push(version)

        if is_ok(result):
            print(f"✅ {result.unwrap()}")
            success_count += 1
        else:
            print(f"❌ {result.unwrap_err()}")
        print()

    if success_count < len(versions):
        return Err(f"Push incomplete: only {success_count}/{len(versions)} succeeded")
    return Ok(f"Push complete: {success_count}/{len(versions)} succeeded")


if __name__ == "__main__":
    main()
