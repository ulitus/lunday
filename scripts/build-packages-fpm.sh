#!/usr/bin/env bash
set -euo pipefail

# Build DEB and RPM packages for Lunday using FPM
# This is a simpler approach than traditional debian/rpm packaging

VERSION="1.0.1"
APP_NAME="lunday"
MAINTAINER="Ulitus <ulitus@users.noreply.github.com>"
HOMEPAGE="https://github.com/ulitus/lunday"
DESCRIPTION="Unofficial Monday.com desktop app for Linux"

BUILD_DIR="${1:-./dist}"
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

mkdir -p "${BUILD_DIR}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Building Lunday Packages with FPM ===${NC}"

# Check if fpm is installed
if ! command -v fpm &> /dev/null; then
    echo -e "${BLUE}Installing fpm...${NC}"
    sudo apt-get update
    sudo apt-get install -y ruby-dev
    sudo gem install fpm -q
fi

# Setup staging directory
echo -e "${BLUE}Preparing staging directory...${NC}"
STAGING="${TEMP_DIR}/staging"
mkdir -p "${STAGING}/usr/local/bin"
mkdir -p "${STAGING}/usr/local/share/applications"
mkdir -p "${STAGING}/usr/local/share/metainfo"
mkdir -p "${STAGING}/usr/local/share/icons/hicolor/scalable/apps"
mkdir -p "${STAGING}/usr/local/share/sounds"

# Copy files
cp assets/lunday.py "${STAGING}/usr/local/bin/lunday"
chmod 755 "${STAGING}/usr/local/bin/lunday"
cp assets/io.github.ulitus.Lunday.desktop "${STAGING}/usr/local/share/applications/"
cp assets/io.github.ulitus.Lunday.metainfo.xml "${STAGING}/usr/local/share/metainfo/"
cp assets/io.github.ulitus.Lunday.svg "${STAGING}/usr/local/share/icons/hicolor/scalable/apps/"
cp assets/notify.wav "${STAGING}/usr/local/share/sounds/"

# Build DEB package
echo -e "${BLUE}Building DEB package...${NC}"
fpm -s dir \
    -t deb \
    -n "${APP_NAME}" \
    -v "${VERSION}" \
    -m "${MAINTAINER}" \
    -d "python3" \
    -d "python3-gi" \
    -d "gir1.2-gtk-4.0" \
    -d "gir1.2-webkit2-4.1" \
    -d "gir1.2-secret-1" \
    -d "gir1.2-gstreamer-1.0" \
    --description "${DESCRIPTION}" \
    -C "${STAGING}" \
    -p "${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb" \
    .

echo -e "${GREEN}✓ DEB package created: ${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb${NC}"

# Build RPM package
echo -e "${BLUE}Building RPM package...${NC}"
fpm -s dir \
    -t rpm \
    -n "${APP_NAME}" \
    -v "${VERSION}" \
    -m "${MAINTAINER}" \
    -d "python3" \
    -d "python3-gobject" \
    -d "gtk4" \
    -d "webkit2-gtk4" \
    -d "libsecret" \
    -d "gstreamer1-plugins-base" \
    --description "${DESCRIPTION}" \
    -C "${STAGING}" \
    -p "${BUILD_DIR}/${APP_NAME}-${VERSION}-1.x86_64.rpm" \
    .

echo -e "${GREEN}✓ RPM package created: ${BUILD_DIR}/${APP_NAME}-${VERSION}-1.x86_64.rpm${NC}"

echo -e "${GREEN}=== Build Complete ===${NC}"
echo -e "${BLUE}Packages:${NC}"
ls -lh "${BUILD_DIR}"/*.{deb,rpm} 2>/dev/null || true

echo ""
echo -e "${BLUE}To install:${NC}"
echo "  Debian/Ubuntu: sudo dpkg -i ${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb"
echo "  RedHat/Fedora: sudo rpm -i ${BUILD_DIR}/${APP_NAME}-${VERSION}-1.x86_64.rpm"
