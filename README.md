# Monday Flatpak (Linux)

This project packages an unofficial monday.com desktop client as a Flatpak using GTK4 + WebKit.

## Prerequisites

Install Flatpak + builder tools:

```bash
sudo apt update
sudo apt install -y flatpak flatpak-builder
```

Install required runtimes:

```bash
flatpak install -y flathub org.gnome.Platform//50 org.gnome.Sdk//50
```

## Build

```bash
cd ~/Desktop/monday-flatpak
chmod +x scripts/build.sh scripts/install-local.sh
./scripts/build.sh
```

This creates:

- `repo/` local Flatpak repository
- `com.monday.Monday.flatpak` standalone bundle

## Install locally

```bash
./scripts/install-local.sh
```

## Run

```bash
flatpak run com.monday.Monday
```

## Notes

- This is an unofficial wrapper, not an official monday.com desktop release.
- Default URL is `https://auth.monday.com/login` and can be changed in `assets/monday.py`.
- Session cookies and website data are stored persistently, so you should stay logged in between app restarts.
- Flatpak permission `org.freedesktop.secrets` is enabled for keyring-backed credential flows.
