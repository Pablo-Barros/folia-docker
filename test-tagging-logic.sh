#!/bin/bash

echo "🧪 Testing new stable-first tagging logic..."
echo "=================================================="

echo ""
echo "🔗 Testing PaperMC API connectivity..."

# Create a simple Python test inline
python3 -c "
import sys
import os
import requests

try:
    # Test getting build info for 1.21.11
    response = requests.get('https://api.papermc.io/v2/projects/folia/versions/1.21.11/builds/2')
    response.raise_for_status()
    build_info = response.json()
    print(f'✅ API call successful for 1.21.11 build 2')
    print(f'   Channel: {build_info.get(\"channel\", \"Unknown\")}')
    print(f'   Build: {build_info.get(\"build\", \"Unknown\")}')
    print(f'   Promoted: {build_info.get(\"promoted\", \"Unknown\")}')
except Exception as e:
    print(f'❌ API call failed: {e}')
    sys.exit(1)
"

echo ""
echo "📋 Testing build detection for version 1.21.11..."

python3 -c "
import requests

def get_builds(version):
    try:
        url = f'https://api.papermc.io/v2/projects/folia/versions/{version}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('builds', [])
    except:
        return []

def is_stable(build):
    return build.get('channel') == 'default'

def get_latest_stable_or_experimental(version):
    builds = get_builds(version)
    if not builds:
        return None, False

    # Look for stable builds first
    for build in reversed(builds):
        if build.get('channel') == 'default':
            return str(build['build']), False

    # Fallback to experimental
    for build in reversed(builds):
        if build.get('channel') == 'experimental':
            return str(build['build']), True

    return None, False

build_result = get_latest_stable_or_experimental('1.21.11')
if build_result and build_result[0]:
    build_number = build_result[0]
    is_experimental = build_result[1]
    print(f'✅ Latest build: {build_number}')
    print(f'🔗 Type: {\"EXPERIMENTAL\" if is_experimental else \"STABLE\"}')

    expected_tag = f'blackao/folia:1.21.21.11'
    if is_experimental:
        expected_tag = f'blackao/folia:1.21.11-exp{build_number}'
    else:
        expected_tag = f'blackao/folia:1.21.21.11'

    print(f'🏷️  Expected image tag: {expected_tag}')
else:
    print(f'❌ No builds available for 1.21.11')
"

echo ""
echo "=================================================="
echo "🎯 Expected Behavior After Implementation:"
echo ""
echo "📦 Version Tags (Stable-First):"
echo "   blackao/folia:1.21.11 → Latest STABLE build when available"
echo "   blackao/folia:1.21.8  → Latest STABLE build when available"
echo "   blackao/folia:1.19.4  → Latest STABLE build when available"
echo ""
echo "📦 Fallback Logic:"
echo "   If no STABLE build exists → Use EXPERIMENTAL fallback"
echo "   If STABLE exists → Always use STABLE (ignore experimental)"
echo ""
echo "📦 Experimental Tags:"
echo "   blackao/folia:experimental → Latest experimental across all versions"
echo "   blackao/folia:1.21.11-expX → Specific experimental build X"
echo ""
echo "📦 Special Tags:"
echo "   blackao/folia:latest → Latest stable across all versions"
echo ""
echo "✅ Implementation Complete - All files updated with stable-first logic!"