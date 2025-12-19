#!/usr/bin/env python3

import argparse
import os

import requests
from result import Err, Ok, Result, is_err


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Folia Download Script - Supports Experimental Builds"
    )

    parser.add_argument(
        "--version",
        type=str,
        default=os.environ.get("VERSION", "latest"),
        help='Minecraft Version (Default: environment variable VERSION or "latest")',
    )

    parser.add_argument(
        "--build",
        type=str,
        default=os.environ.get("BUILD", "latest"),
        help='Build Number (Default: environment variable BUILD or "latest")',
    )

    parser.add_argument(
        "--channel",
        type=str,
        default=os.environ.get("CHANNEL", "default"),
        choices=["default", "experimental"],
        help='Release channel (Default: environment variable CHANNEL or "default")',
    )

    parser.add_argument(
        "--output",
        type=str,
        default="server.jar",
        help="Output file path (Default: server.jar)",
    )

    args = parser.parse_args()

    if args.version == "latest":
        version_result = get_latest_version(args.channel)
        if is_err(version_result):
            print(f"Error: {version_result.unwrap_err()}")
            exit(1)
        version = version_result.unwrap()
    else:
        version = args.version

    if args.build == "latest":
        build_result = get_latest_build(version, args.channel)
        if is_err(build_result):
            print(f"Error: {build_result.unwrap_err()}")
            exit(1)
        build = build_result.unwrap()
    else:
        build = args.build

    print(f"Version: {version}")
    print(f"Build: {build}")
    print(f"Channel: {args.channel}")

    download_result = download_folia(version, build, args.output)
    if is_err(download_result):
        print(f"Error: {download_result.unwrap_err()}")
        exit(1)


def download_folia(
    version: str, build: str, output: str = "server.jar"
) -> Result[None, str]:
    base_url = "https://api.papermc.io/v2/projects/folia"
    download_url = f"{base_url}/versions/{version}/builds/{build}/downloads/folia-{version}-{build}.jar"

    try:
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        response = requests.get(download_url)
        response.raise_for_status()

        with open(output, "wb") as f:
            f.write(response.content)

        print(f"Downloaded: {os.path.basename(output)}")
        return Ok(None)
    except Exception as e:
        return Err(f"Error downloading: {e}")


def get_latest_version(channel: str = "default") -> Result[str, str]:
    base_url = "https://api.papermc.io/v2/projects/folia"

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        versions = data["versions"]

        # Try versions in reverse order (newest first)
        for version in reversed(versions):
            build_result = get_latest_build(version, channel)
            if not is_err(build_result):
                return Ok(version)

        return Err(f"No version with available builds found for channel: {channel}")
    except Exception as e:
        return Err(f"Error getting latest version: {e}")


def get_latest_build(version: str, channel: str = "default") -> Result[str, str]:
    base_url = "https://api.papermc.io/v2/projects/folia"

    try:
        response = requests.get(f"{base_url}/versions/{version}")
        response.raise_for_status()
        data = response.json()

        builds = data.get("builds", [])
        if not builds:
            return Err(f"No builds found for version {version}")

        # Filter builds by channel if specified
        if channel != "default":
            channel_builds = []
            for build_info in builds:
                if isinstance(build_info, dict) and build_info.get("channel") == channel:
                    channel_builds.append(build_info)

            if channel_builds:
                # Return the build number from the last channel build
                latest_channel_build = channel_builds[-1]
                return Ok(str(latest_channel_build["build"]))
            else:
                return Err(f"No {channel} builds found for version {version}")

        # For "default" channel, return the last build
        return Ok(str(builds[-1]))
    except Exception as e:
        return Err(f"Error getting latest build for version {version}: {e}")


def get_build_details(version: str, build: str) -> Result[dict, str]:
    """Get detailed information about a specific build."""
    base_url = "https://api.papermc.io/v2/projects/folia"

    try:
        response = requests.get(f"{base_url}/versions/{version}/builds/{build}")
        response.raise_for_status()
        return Ok(response.json())
    except Exception as e:
        return Err(f"Error getting build details for {version} build {build}: {e}")


if __name__ == "__main__":
    main()