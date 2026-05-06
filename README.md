# Lunday

An unofficial Monday.com desktop app for Linux, packaged as a Flatpak using GTK4 + WebKit.

## Install

### Flatpak (recommended)

Add the Lunday Flatpak remote and install in one step:

```bash
curl -s https://raw.githubusercontent.com/ulitus/lunday/main/scripts/add-remote.sh | bash
```

To update in the future:

```bash
flatpak update io.github.ulitus.Lunday
```

### Debian/Ubuntu

Download the DEB package from the [latest release](https://github.com/ulitus/lunday/releases) and install:

```bash
sudo dpkg -i lunday_1.0.1_amd64.deb
```

Or install directly:

```bash
sudo apt update
sudo apt install ./lunday_1.0.1_amd64.deb
```

### Red Hat/Fedora/CentOS

Download the RPM package from the [latest release](https://github.com/ulitus/lunday/releases) and install:

```bash
sudo rpm -i lunday-1.0.1-1.x86_64.rpm
```

Or using dnf:

```bash
sudo dnf install ./lunday-1.0.1-1.x86_64.rpm
```

## Build from source

### Prerequisites

```bash
sudo apt update
sudo apt install -y flatpak flatpak-builder
flatpak install -y flathub org.gnome.Platform//50 org.gnome.Sdk//50
```

### Build

```bash
cd ~/Desktop/lunday-flatpak
chmod +x scripts/build.sh scripts/install-local.sh
./scripts/build.sh
```

This creates:

- `repo/` local Flatpak repository
- `io.github.ulitus.Lunday.flatpak` standalone bundle

### Install locally

```bash
./scripts/install-local.sh
```

### Build DEB and RPM packages

To create distributable DEB and RPM packages:

```bash
chmod +x scripts/build-packages-fpm.sh
./scripts/build-packages-fpm.sh ./dist
```

This creates:

- `dist/lunday_1.0.1_amd64.deb` - Debian/Ubuntu package
- `dist/lunday-1.0.1-1.x86_64.rpm` - Red Hat/Fedora package

Then install using:

```bash
# Debian/Ubuntu
sudo dpkg -i dist/lunday_1.0.1_amd64.deb

# Red Hat/Fedora
sudo rpm -i dist/lunday-1.0.1-1.x86_64.rpm
```

## Run

```bash
flatpak run io.github.ulitus.Lunday
```

## Notes

- This is an unofficial wrapper, not an official monday.com desktop release.
- Default URL is `https://auth.monday.com/login` and can be changed in `assets/lunday.py`.
- Session cookies and website data are stored persistently, so you should stay logged in between app restarts.
- Flatpak permission `org.freedesktop.secrets` is enabled for keyring-backed credential flows.
