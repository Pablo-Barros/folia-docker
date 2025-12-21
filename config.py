import os
from typing import Optional

class DockerConfig:
    """Centralized configuration for Docker image naming and build settings."""

    @staticmethod
    def get_namespace() -> str:
        """Get the Docker namespace from environment variable or default."""
        return os.environ.get('DOCKER_NAMESPACE', 'blackao')

    @staticmethod
    def get_image_name(tag: str) -> str:
        """Generate the full Docker image name with namespace and tag."""
        namespace = DockerConfig.get_namespace()
        return f"{namespace}/folia:{tag}"

    @staticmethod
    def get_registry_url() -> Optional[str]:
        """Get custom Docker registry URL if configured."""
        return os.environ.get('DOCKER_REGISTRY_URL')

    @staticmethod
    def get_full_image_name(tag: str) -> str:
        """Get the full image name including registry if configured."""
        image_name = DockerConfig.get_image_name(tag)
        registry = DockerConfig.get_registry_url()

        if registry:
            return f"{registry}/{image_name}"
        return image_name


class BuildConfig:
    """Configuration for build processes."""

    @staticmethod
    def is_experimental_enabled() -> bool:
        """Check if experimental build support is enabled."""
        return os.environ.get('ENABLE_EXPERIMENTAL', 'false').lower() == 'true'

    @staticmethod
    def get_experimental_channel() -> str:
        """Get the experimental channel name."""
        return os.environ.get('EXPERIMENTAL_CHANNEL', 'experimental')

    @staticmethod
    def auto_sync_experimental() -> bool:
        """Check if experimental versions should be auto-synced."""
        return os.environ.get('AUTO_SYNC_EXPERIMENTAL', 'true').lower() == 'true'


class VersionConfig:
    """Configuration for version management."""

    @staticmethod
    def get_version_tag_pattern(version: str, build: Optional[int] = None, is_experimental: bool = False) -> str:
        """Generate version tag based on type and build number."""
        if is_experimental and build:
            return f"{version}-exp{build}"
        return version

    @staticmethod
    def get_latest_experimental_tag() -> str:
        """Get the tag name for latest experimental build."""
        return "experimental"

    @staticmethod
    def prefer_stable_builds() -> bool:
        """Check if stable builds should be preferred over experimental builds."""
        return os.environ.get('PREFER_STABLE_BUILDS', 'true').lower() == 'true'

    @staticmethod
    def get_default_build_channel() -> str:
        """Get default build channel preference."""
        return os.environ.get('DEFAULT_BUILD_CHANNEL', 'default')

    @staticmethod
    def get_stable_channel_name() -> str:
        """Get the stable channel name."""
        return "default"

    @staticmethod
    def get_experimental_channel_name() -> str:
        """Get the experimental channel name."""
        return "experimental"