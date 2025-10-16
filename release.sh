#!/bin/bash
# Automated release script for HACS compatibility

if [ "$#" -ne 2 ]; then
    echo "Usage: ./release.sh <version> <description>"
    echo "Example: ./release.sh 1.1.3 'Fix power data parsing'"
    exit 1
fi

VERSION="$1"
DESCRIPTION="$2"

echo "Creating release v${VERSION}..."

# Update version in manifest.json
sed -i '' "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" custom_components/sense/manifest.json

# Update CHANGELOG.md
DATE=$(date +%Y-%m-%d)
sed -i '' "7i\\
## [${VERSION}] - ${DATE}\\
\\
### Changed\\
- ${DESCRIPTION}\\
\\
" CHANGELOG.md

# Git operations
git add -A
git commit -m "Release v${VERSION}: ${DESCRIPTION}"
git push origin main
git tag -a "v${VERSION}" -m "Release v${VERSION}: ${DESCRIPTION}"
git push origin "v${VERSION}"

# Create GitHub release
gh release create "v${VERSION}" --title "v${VERSION}" --notes "${DESCRIPTION}"

echo "✅ Release v${VERSION} created successfully!"

