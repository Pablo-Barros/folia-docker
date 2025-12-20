#!/bin/bash

# Script to create directories for all available Folia versions
# Based on PaperMC API: https://api.papermc.io/v2/projects/folia

echo "Creating directories for all Folia versions..."

# Array of versions to create (all experimental)
VERSIONS=(
    "1.19.4:39"
    "1.20.1:latest"
    "1.20.2:latest"
    "1.20.4:latest"
    "1.20.6:latest"
    "1.21.4:latest"
    "1.21.5:latest"
    "1.21.6:latest"
    "1.21.8:6"
    "1.21.11:2"
)

for VERSION_INFO in "${VERSIONS[@]}"; do
    IFS=':' read -r VERSION BUILD <<< "$VERSION_INFO"

    echo "Creating directory for Folia $VERSION (build: $BUILD)..."

    # Create directory
    mkdir -p "versions/$VERSION"

    # Copy template files
    cp "versions/latest/Dockerfile" "versions/$VERSION/"
    cp "versions/latest/entrypoint.sh" "versions/$VERSION/"
    cp "versions/latest/requirements.txt" "versions/$VERSION/"
    cp "versions/latest/get-folia.py" "versions/$VERSION/"

    # Create README.md for experimental version
    cat > "versions/$VERSION/README.md" << EOF
# Folia $VERSION (Experimental)

This Docker image provides Folia Minecraft server version $VERSION (experimental build).

**Build:** $BUILD
**Channel:** experimental

## Quick start

\`\`\`bash
docker run -it -d -p 25565:25565 --name folia-$VERSION -e MINECRAFT_EULA=true blackao/folia:$VERSION
\`\`\`

## Environment variables

- \`MIN_RAM\` (default: 512M) - Minimum RAM allocated for the server
- \`MAX_RAM\` (default: 1G) - Maximum RAM allocated for the server
- \`MINECRAFT_EULA\` (default: false) - Set to \`true\` to accept the Minecraft EULA
- \`JAVA_FLAGS\` - Additional Java flags
- \`FOLIA_FLAGS\` (default: --nojline) - Custom Folia server flags
- \`TZ\` (example: Europe/Berlin) - Set the time zone for the server

## Build from source

\`\`\`bash
docker build --build-arg VERSION=$VERSION --build-arg BUILD=$BUILD -t blackao/folia:$VERSION versions/$VERSION/
\`\`\`

## Experimental Build Warning

This is an experimental build of Folia. Experimental builds may contain new features but can also have bugs. Use with caution in production environments.

## License

This project is licensed under the terms of the GNU General Public License v3.0 License.
EOF

    echo "✅ Created directory for Folia $VERSION"
done

echo ""
echo "All directories created successfully!"
echo ""
echo "Available versions:"
for VERSION_INFO in "${VERSIONS[@]}"; do
    IFS=':' read -r VERSION BUILD <<< "$VERSION_INFO"
    echo "- Folia $VERSION (build: $BUILD)"
done
echo ""
echo "Next step: Run the build script to build all images:"
echo "./build-all-images.sh"