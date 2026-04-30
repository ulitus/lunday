#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.lunday.Lunday"
MANIFEST="com.lunday.Lunday.yml"
BUILD_DIR="build-dir"
REPO_DIR="repo"

flatpak-builder --force-clean --repo="${REPO_DIR}" "${BUILD_DIR}" "${MANIFEST}"
flatpak build-bundle "${REPO_DIR}" "${APP_ID}.flatpak" "${APP_ID}"

echo "Build complete: ${APP_ID}.flatpak"
