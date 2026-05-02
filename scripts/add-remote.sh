#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# Lunday — add Flatpak remote and install
# Run this once to set up Lunday and get automatic updates via:
#   flatpak update io.github.ulitus.Lunday
# ─────────────────────────────────────────────────────────────────
set -euo pipefail

REMOTE_NAME="lunday"
REMOTE_URL="https://ulitus.github.io/lunday/"
APP_ID="io.github.ulitus.Lunday"

echo "Adding Lunday Flatpak remote…"
flatpak remote-add --user --if-not-exists --no-gpg-verify \
    "${REMOTE_NAME}" "${REMOTE_URL}"

echo "Installing ${APP_ID}…"
flatpak install --user -y "${REMOTE_NAME}" "${APP_ID}"

echo ""
echo "Done! Run Lunday with:"
echo "  flatpak run ${APP_ID}"
echo ""
echo "To update in the future:"
echo "  flatpak update ${APP_ID}"
