#!/usr/bin/env bash
set -euo pipefail

# Build both DEB and RPM packages for Lunday

BUILD_DIR="${1:-./dist}"
VERSION="1.0.1"
APP_NAME="lunday"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Building Lunday DEB and RPM Packages ===${NC}"

# Create build directory
mkdir -p "${BUILD_DIR}"

# Check dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    if ! command -v dpkg-buildpackage &> /dev/null; then
        echo "Installing dpkg-dev..."
        sudo apt-get update
        sudo apt-get install -y dpkg-dev devscripts debhelper
    fi
    
    if ! command -v rpmbuild &> /dev/null; then
        echo "Installing rpm build tools..."
        sudo apt-get install -y rpm
    fi
    
    if ! command -v fakeroot &> /dev/null; then
        echo "Installing fakeroot..."
        sudo apt-get install -y fakeroot
    fi
}

# Build DEB package
build_deb() {
    echo -e "${BLUE}Building DEB package...${NC}"
    
    # Create a temporary directory for building
    TEMP_DEB=$(mktemp -d)
    trap "rm -rf ${TEMP_DEB}" EXIT
    
    # Copy source to temp directory
    cp -r . "${TEMP_DEB}/lunday-${VERSION}"
    cd "${TEMP_DEB}/lunday-${VERSION}"
    
    # Build the package
    dpkg-buildpackage -us -uc -b
    
    # Copy the built deb to output directory
    cp "${TEMP_DEB}/"*.deb "${BUILD_DIR}/"
    
    echo -e "${GREEN}DEB package built successfully!${NC}"
}

# Build RPM package using alien (convert from deb)
build_rpm_from_deb() {
    echo -e "${BLUE}Building RPM package from DEB (using alien)...${NC}"
    
    if ! command -v alien &> /dev/null; then
        echo "Installing alien..."
        sudo apt-get install -y alien
    fi
    
    # Convert deb to rpm
    for deb in "${BUILD_DIR}"/${APP_NAME}_*.deb; do
        if [ -f "$deb" ]; then
            alien --to-rpm --keep-version "$deb"
            mv "${APP_NAME}-"*.rpm "${BUILD_DIR}/" 2>/dev/null || true
        fi
    done
    
    echo -e "${GREEN}RPM package built successfully!${NC}"
}

# Build RPM package directly (alternative method)
build_rpm_direct() {
    echo -e "${BLUE}Building RPM package directly...${NC}"
    
    TEMP_RPM=$(mktemp -d)
    trap "rm -rf ${TEMP_RPM}" EXIT
    
    # Create RPM build directories
    mkdir -p "${TEMP_RPM}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
    
    # Copy spec file
    cp rpm/lunday.spec "${TEMP_RPM}/SPECS/"
    
    # Create source tarball
    tar czf "${TEMP_RPM}/SOURCES/lunday-${VERSION}.tar.gz" \
        --exclude='.git' \
        --exclude='build-dir' \
        --exclude='flathub-build' \
        --exclude='repo' \
        --exclude='dist' \
        .
    
    # Build RPM
    rpmbuild -ba \
        --define "_topdir ${TEMP_RPM}" \
        --define "_version ${VERSION}" \
        "${TEMP_RPM}/SPECS/lunday.spec"
    
    # Copy built RPM to output directory
    cp "${TEMP_RPM}"/RPMS/**/*.rpm "${BUILD_DIR}/" 2>/dev/null || true
    
    echo -e "${GREEN}RPM package built successfully!${NC}"
}

# Main execution
check_dependencies

# Build DEB
build_deb

# Build RPM (try alien first, fall back to direct method)
if command -v alien &> /dev/null; then
    build_rpm_from_deb
else
    build_rpm_direct
fi

# Summary
echo -e "${GREEN}=== Build Complete ===${NC}"
echo -e "${BLUE}Packages created in: ${BUILD_DIR}${NC}"
echo -e "${BLUE}Contents:${NC}"
ls -lh "${BUILD_DIR}"/*.{deb,rpm} 2>/dev/null || true

echo -e "${GREEN}✓ Ready to install!${NC}"
echo ""
echo "To install the DEB package:"
echo "  sudo dpkg -i ${BUILD_DIR}/${APP_NAME}_${VERSION}-*.deb"
echo ""
echo "To install the RPM package:"
echo "  sudo rpm -i ${BUILD_DIR}/${APP_NAME}-${VERSION}-*.rpm"
