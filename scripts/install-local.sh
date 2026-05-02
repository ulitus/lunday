#!/usr/bin/env bash
set -euo pipefail

APP_ID="io.github.ulitus.Lunday"
REPO_DIR="repo"

flatpak --user remote-add --if-not-exists --no-gpg-verify lunday-local "${REPO_DIR}"
flatpak --user install -y lunday-local "${APP_ID}"

echo "Installed ${APP_ID} from local repo."
