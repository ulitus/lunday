Name:           lunday
Version:        1.0.1
Release:        1%{?dist}
Summary:        Unofficial Monday.com desktop app for Linux

License:        GPL-3.0+
URL:            https://github.com/ulitus/lunday
Source0:        https://github.com/ulitus/lunday/archive/refs/heads/main.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3 python3-gobject gtk4 webkit2-gtk4 libsecret gstreamer1

%description
Lunday is an unofficial Monday.com desktop application for Linux,
built with GTK4 and WebKit. It provides a native desktop experience
for Monday.com project management platform.

%install
mkdir -p %{buildroot}/usr/local/bin
mkdir -p %{buildroot}/usr/local/share/applications
mkdir -p %{buildroot}/usr/local/share/metainfo
mkdir -p %{buildroot}/usr/local/share/icons/hicolor/scalable/apps
mkdir -p %{buildroot}/usr/local/share/sounds

install -Dm755 assets/lunday.py %{buildroot}/usr/local/bin/lunday
install -Dm644 assets/io.github.ulitus.Lunday.desktop %{buildroot}/usr/local/share/applications/io.github.ulitus.Lunday.desktop
install -Dm644 assets/io.github.ulitus.Lunday.metainfo.xml %{buildroot}/usr/local/share/metainfo/io.github.ulitus.Lunday.metainfo.xml
install -Dm644 assets/io.github.ulitus.Lunday.svg %{buildroot}/usr/local/share/icons/hicolor/scalable/apps/io.github.ulitus.Lunday.svg
install -Dm644 assets/notify.wav %{buildroot}/usr/local/share/sounds/notify.wav

%files
/usr/local/bin/lunday
/usr/local/share/applications/io.github.ulitus.Lunday.desktop
/usr/local/share/metainfo/io.github.ulitus.Lunday.metainfo.xml
/usr/local/share/icons/hicolor/scalable/apps/io.github.ulitus.Lunday.svg
/usr/local/share/sounds/notify.wav

%changelog
* Tue May 06 2026 Ulitus <ulitus@users.noreply.github.com> - 1.0.1-1
- Initial RPM package release
