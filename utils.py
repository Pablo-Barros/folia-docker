import os
import re
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
    if version == "latest-experimental":
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
                    if version == "latest-experimental":
                        experimental_tags.append("latest-experimental")
                    elif "experimental" in content:
                        # Add experimental tag format
                        experimental_tags.append(f"{version}-exp*")
            except Exception:
                pass

    return experimental_tags
