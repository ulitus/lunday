# Lunday

An unofficial Monday.com desktop app for Linux, packaged as a Flatpak using GTK4 + WebKit.

## Install (recommended)

Add the Lunday Flatpak remote and install in one step:

```bash
curl -s https://raw.githubusercontent.com/ulitus/lunday/main/scripts/add-remote.sh | bash
```

To update in the future:

```bash
flatpak update io.github.ulitus.Lunday
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

## Run

```bash
flatpak run io.github.ulitus.Lunday
```

## Notes

- This is an unofficial wrapper, not an official monday.com desktop release.
- Default URL is `https://auth.monday.com/login` and can be changed in `assets/lunday.py`.
- Session cookies and website data are stored persistently, so you should stay logged in between app restarts.
- Flatpak permission `org.freedesktop.secrets` is enabled for keyring-backed credential flows.
