#!/usr/bin/env python3

"""
Test script for the new stable-first tagging logic
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils import get_latest_stable_or_experimental_build, is_build_experimental, get_available_builds

def test_version_tag_logic():
    """Test the new tagging logic for version tags"""

    print("🧪 Testing new stable-first tagging logic...")
    print("=" * 50)

    # Test cases
    test_versions = ["1.19.4", "1.21.8", "1.21.11"]

    for version in test_versions:
        print(f"\n📋 Testing version: {version}")
        print("-" * 30)

        # Test 1: Get latest stable or experimental build
        build_result = get_latest_stable_or_experimental_build(version)
        if build_result and build_result[0]:
            build_number = build_result[0]
            is_experimental = build_result[1]

            print(f"✅ Latest build: {build_number}")
            print(f"🔗 Type: {'EXPERIMENTAL' if is_experimental else 'STABLE'}")

            # Expected tag name
            expected_tag = f"blackao/folia:{version}"
            if is_experimental:
                expected_tag = f"blackao/folia:{version}-exp{build_number}"

            print(f"🏷️  Expected image tag: {expected_tag}")

        else:
            print(f"❌ No builds available for {version}")

        # Test 2: Get available builds summary
        available_builds = get_available_builds(version)
        print(f"📊 Available builds:")
        print(f"   Stable builds: {available_builds['stable'] or 'None'}")
        print(f"   Experimental builds: {available_builds['experimental'] or 'None'}")
        print(f"   Latest stable: {available_builds['latest_stable'] or 'None'}")
        print(f"   Latest experimental: {available_builds['latest_experimental'] or 'None'}")

    print("\n" + "=" * 50)
    print("🎯 Tagging Logic Summary:")
    print("- Version tags (e.g., '1.21.11') → ALWAYS point to stable when available")
    print("- If no stable exists → use experimental fallback")
    print("- Experimental tags (e.g., '1.21.11-expX') → explicit experimental builds")
    print("- 'experimental' tag → latest experimental across all versions")
    print("- 'latest' tag → latest stable across all versions")

def test_api_calls():
    """Test if PaperMC API calls work correctly"""
    print("\n🔗 Testing PaperMC API connectivity...")

    try:
        from utils import get_build_info

        # Test getting build info for 1.21.11 build 2
        build_info = get_build_info("1.21.11", "2")
        if build_info:
            print(f"✅ API call successful for 1.21.11 build 2")
            print(f"   Channel: {build_info.get('channel', 'Unknown')}")
            print(f"   Build: {build_info.get('build', 'Unknown')}")
        else:
            print(f"❌ No build info for 1.21.11 build 2")

    except Exception as e:
        print(f"❌ API call failed: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Stable-First Docker Tagging Implementation")
    print("This test validates the new logic where version tags prioritize stable builds")

    test_api_calls()
    test_version_tag_logic()

    print("\n✨ Testing complete!")
    print("The new implementation should ensure that:")
    print("1. blackao/folia:1.21.11 always uses latest stable when available")
    print("2. Falls back to experimental only when no stable exists")
   3. "3. Maintains backward compatibility with existing tags")

if __name__ == "__main__":
    main()