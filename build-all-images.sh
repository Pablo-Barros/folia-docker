#!/bin/bash

# Build script for all Folia Docker images
# All versions are experimental builds from PaperMC API

echo "Starting build of all Folia Docker images..."
echo "Note: All Folia versions are currently experimental builds"

# Array of versions to build (version:build)
declare -A VERSIONS=(
    ["1.19.4"]="39"
    ["1.20.1"]="latest"
    ["1.20.2"]="latest"
    ["1.20.4"]="latest"
    ["1.20.6"]="latest"
    ["1.21.4"]="latest"
    ["1.21.5"]="latest"
    ["1.21.6"]="latest"
    ["1.21.8"]="6"
    ["1.21.11"]="2"
)

# Build all versions
echo "Building all Folia versions..."
for VERSION in "${!VERSIONS[@]}"; do
    BUILD="${VERSIONS[$VERSION]}"
    echo "Building Folia $VERSION (build: $BUILD)..."

    if [ "$BUILD" = "latest" ]; then
        docker build -t blackao/folia:$VERSION ./versions/$VERSION/
    else
        docker build -t blackao/folia:$VERSION --build-arg VERSION=$VERSION --build-arg BUILD=$BUILD ./versions/$VERSION/
    fi

    if [ $? -eq 0 ]; then
        echo "✅ Successfully built: blackao/folia:$VERSION"
    else
        echo "❌ Failed to build: blackao/folia:$VERSION"
        exit 1
    fi
done

# Tag newest version (1.21.11) as latest
echo "Tagging 1.21.11 as latest..."
docker tag blackao/folia:1.21.11 blackao/folia:latest

# Tag 1.21.11 as experimental
echo "Tagging 1.21.11 as experimental..."
docker tag blackao/folia:1.21.11 blackao/folia:experimental

# Create version-specific experimental tag for 1.21.11
echo "Creating version-specific experimental tag..."
docker tag blackao/folia:1.21.11 blackao/folia:1.21.11-exp2

echo "Build complete! Pushing images to Docker Hub..."

# Push all version tags
echo "Pushing all versions..."
for VERSION in "${!VERSIONS[@]}"; do
    echo "Pushing blackao/folia:$VERSION..."
    docker push blackao/folia:$VERSION

    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed: blackao/folia:$VERSION"
    else
        echo "❌ Failed to push: blackao/folia:$VERSION"
    fi
done

# Push special tags
echo "Pushing special tags..."
docker push blackao/folia:latest
docker push blackao/folia:experimental
docker push blackao/folia:1.21.11-exp2

echo ""
echo "🎉 All images built and pushed successfully!"
echo ""
echo "📋 Available tags:"
echo "🔹 Version tags:"
for VERSION in $(printf '%s\n' "${!VERSIONS[@]}" | sort); do
    echo "   - blackao/folia:$VERSION (build: ${VERSIONS[$VERSION]})"
done
echo ""
echo "🔹 Special tags:"
echo "   - blackao/folia:latest (points to 1.21.11)"
echo "   - blackao/folia:experimental (points to 1.21.11)"
echo "   - blackao/folia:1.21.11-exp2 (version-specific experimental)"
echo ""
echo "📝 Note: All Folia versions are currently experimental builds"
echo "🚀 Ready to use with: docker run -d -p 25565:25565 -e MINECRAFT_EULA=true blackao/folia:latest"