import os
import re
import requests
from typing import List, Tuple, Optional

from config import BuildConfig


def _parse_version_key(tag: str) -> Tuple:
    """
    Parse a version tag into a tuple for sorting purposes.
    Handles semantic versioning with pre-release identifiers.

    Args:
        tag: Version tag string (e.g., "1.21.9-pre2", "1.21.9", "latest")

    Returns:
        Tuple: Sortable tuple where "latest" sorts last, and versions sort naturally
    """
    if tag == "latest":
        return (float("inf"),)

    try:
        version_part = tag.split("-")[0]
        version_numbers = [int(x) for x in version_part.split(".")]

        if "-" in tag:
            pre_release = tag.split("-", 1)[1]
            return tuple(version_numbers + [0, pre_release])
        else:
            return tuple(version_numbers + [1])

    except ValueError:
        return (tag,)


def discover_versions() -> List[str]:
    versions = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    versions_dir = os.path.join(current_dir, "versions")

    for item in os.listdir(versions_dir):
        item_path = os.path.join(versions_dir, item)

        if not os.path.isdir(item_path):
            continue

        disabled_file = os.path.join(item_path, ".disabled")

        if os.path.exists(disabled_file):
            continue

        # Skip experimental versions if experimental builds are disabled
        if not BuildConfig.is_experimental_enabled() and _is_experimental_version(item):
            continue

        versions.append(item)

    def sort_key(version: str) -> str:
        return _parse_version_key(version)

    return sorted(versions, key=sort_key)


def discover_experimental_versions() -> List[str]:
    """Discover only experimental versions."""
    if not BuildConfig.is_experimental_enabled():
        return []

    versions = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    versions_dir = os.path.join(current_dir, "versions")

    for item in os.listdir(versions_dir):
        item_path = os.path.join(versions_dir, item)

        if not os.path.isdir(item_path):
            continue

        disabled_file = os.path.join(item_path, ".disabled")
        if os.path.exists(disabled_file):
            continue

        if _is_experimental_version(item):
            versions.append(item)

    def sort_key(version: str) -> str:
        return _parse_version_key(version)

    return sorted(versions, key=sort_key)


def _is_experimental_version(version: str) -> bool:
    """Check if a version is experimental."""
    # Check for explicit experimental directories
    if version == "experimental":
        return True

    # Check version directory for experimental build markers
    version_dir = os.path.join(os.path.dirname(__file__), "versions", version)

    # Check if get-folia.py is the enhanced version that supports channels
    get_folia_path = os.path.join(version_dir, "get-folia.py")
    if os.path.exists(get_folia_path):
        try:
            with open(get_folia_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for channel parameter or experimental mentions
                if "--channel" in content or "experimental" in content:
                    return True
        except Exception:
            pass

    # Check README.md for experimental mentions
    readme_path = os.path.join(version_dir, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if "experimental" in content:
                    return True
        except Exception:
            pass

    return False


def get_experimental_tags(version: str) -> List[str]:
    """Get experimental build tags for a version."""
    if not BuildConfig.is_experimental_enabled():
        return []

    experimental_tags = []

    # Check if this version has experimental builds
    if _is_experimental_version(version):
        # Try to detect experimental build numbers from the version directory
        version_dir = os.path.join(os.path.dirname(__file__), "versions", version)
        get_folia_path = os.path.join(version_dir, "get-folia.py")

        if os.path.exists(get_folia_path):
            try:
                with open(get_folia_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for build number patterns or channel configuration
                    # This is a simple heuristic - could be enhanced with API calls
                    if version == "experimental":
                        experimental_tags.append("experimental")
                    elif "experimental" in content:
                        # Add experimental tag format
                        experimental_tags.append(f"{version}-exp*")
            except Exception:
                pass

    return experimental_tags


# =============================================================================
# Build Detection Functions for Stable-First Tagging Strategy
# =============================================================================

# Simple cache to avoid repeated API calls during build process
_build_info_cache = {}


def get_build_info_cached(version: str, build: str) -> dict:
    """
    Cached version of get_build_info to avoid repeated API calls.

    Args:
        version: Folia version (e.g., "1.21.11")
        build: Build number (e.g., "2")

    Returns:
        Dictionary containing build information, or empty dict on error
    """
    cache_key = f"{version}-{build}"
    if cache_key not in _build_info_cache:
        _build_info_cache[cache_key] = get_build_info(version, build)
    return _build_info_cache[cache_key]

def get_build_info(version: str, build: str) -> dict:
    """
    Get build information including channel from PaperMC API.

    Args:
        version: Folia version (e.g., "1.21.11")
        build: Build number (e.g., "2")

    Returns:
        Dictionary containing build information, or empty dict on error
    """
    try:
        url = f"https://api.papermc.io/v2/projects/folia/versions/{version}/builds/{build}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching build info for {version}-{build}: {e}")
        return {}


def is_build_experimental(version: str, build: str) -> bool:
    """
    Check if a specific build is experimental.

    Args:
        version: Folia version
        build: Build number

    Returns:
        True if build is experimental, False otherwise
    """
    build_info = get_build_info(version, build)
    return build_info.get("channel") == "experimental"


def get_latest_stable_or_experimental_build(version: str) -> Tuple[Optional[str], bool]:
    """
    Get the latest build number for a version, preferring stable over experimental.

    Args:
        version: Folia version

    Returns:
        Tuple of (build_number, is_experimental)
        build_number: Latest build number (or None if no builds)
        is_experimental: True if the build is experimental, False if stable
    """
    try:
        url = f"https://api.papermc.io/v2/projects/folia/versions/{version}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        builds = data.get("builds", [])
        if not builds:
            return None, False

        # Single pass through builds (latest first), collecting stable and experimental
        latest_stable = None
        latest_experimental = None

        for build_num in reversed(builds):
            build_info = get_build_info_cached(version, str(build_num))

            # Skip if build_info is empty or not a dict
            if not build_info or not isinstance(build_info, dict):
                continue

            channel = build_info.get("channel")

            if channel == "default" and latest_stable is None:
                latest_stable = str(build_num)
            elif channel == "experimental" and latest_experimental is None:
                latest_experimental = str(build_num)

            # Early exit if we have both
            if latest_stable and latest_experimental:
                break

        # Return stable if available, otherwise experimental
        if latest_stable:
            return latest_stable, False
        if latest_experimental:
            return latest_experimental, True

        # Fallback: use the latest build number if no channel info found
        return str(builds[-1]), True

    except Exception as e:
        print(f"Error getting build info for {version}: {e}")
        return None, False


def get_latest_build_for_channel(version: str, channel: str = "default") -> Optional[str]:
    """
    Get the latest build number for a specific channel.

    Args:
        version: Folia version
        channel: Build channel ("default" for stable, "experimental" for experimental)

    Returns:
        Latest build number for the channel, or None if not found
    """
    try:
        url = f"https://api.papermc.io/v2/projects/folia/versions/{version}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        builds = data.get("builds", [])
        for build_num in reversed(builds):
            build_info = get_build_info_cached(version, str(build_num))
            if build_info.get("channel") == channel:
                return str(build_num)

        return None

    except Exception as e:
        print(f"Error getting latest build for {version} channel {channel}: {e}")
        return None


def get_available_builds(version: str) -> dict:
    """
    Get all available builds for a version, categorized by channel.

    Args:
        version: Folia version

    Returns:
        Dictionary with 'stable' and 'experimental' build lists
    """
    try:
        url = f"https://api.papermc.io/v2/projects/folia/versions/{version}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        builds = data.get("builds", [])
        stable_builds = []
        experimental_builds = []

        for build_num in builds:
            build_info = get_build_info_cached(version, str(build_num))
            channel = build_info.get("channel", "experimental")  # Default to experimental for safety

            if channel == "default":
                stable_builds.append(str(build_num))
            else:
                experimental_builds.append(str(build_num))

        return {
            "stable": stable_builds,
            "experimental": experimental_builds,
            "latest_stable": stable_builds[-1] if stable_builds else None,
            "latest_experimental": experimental_builds[-1] if experimental_builds else None
        }

    except Exception as e:
        print(f"Error getting builds for {version}: {e}")
        return {"stable": [], "experimental": [], "latest_stable": None, "latest_experimental": None}
