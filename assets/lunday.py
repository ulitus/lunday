#!/usr/bin/env python3

import json
import os
import sys
from urllib.parse import urlparse
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('WebKit', '6.0')
gi.require_version('Secret', '1')
gi.require_version('Gst', '1.0')

from gi.repository import Gdk, Gio, GLib, Gtk, WebKit, Secret, Gst

Gst.init(None)

APP_ID = 'io.github.ulitus.Lunday'
APP_VERSION = '1.0.0'
START_URL = 'https://auth.monday.com/login'
LOGOUT_URL = 'https://auth.monday.com/logout'

DEFAULT_NOTIFICATION_SOUND_NAME = 'Default'
CUSTOM_NOTIFICATION_SOUND_NAME = 'Custom File'
DEFAULT_NOTIFICATION_SOUND_PATH = '/app/share/sounds/notify.wav'

APP_CSS = """
.modern-header {
    padding: 4px 8px;
    background: @theme_bg_color;
    border-bottom: 1px solid alpha(@theme_fg_color, 0.10);
    box-shadow: none;
}

.menu-button,
.nav-button {
    min-width: 26px;
    min-height: 26px;
    border-radius: 9px;
    background: alpha(@theme_fg_color, 0.10);
    border: none;
    box-shadow: none;
}

.workspace-title {
    font-weight: 500;
    letter-spacing: 0;
    font-size: 13px;
    color: @theme_fg_color;
    padding: 0;
}

.workspace-subtitle {
    font-size: 11px;
    color: alpha(@theme_fg_color, 0.70);
    padding: 0;
}

.loading-text {
    font-size: 11px;
    color: alpha(@theme_fg_color, 0.70);
    padding: 0;
}

.content-card {
    margin: 8px 16px 16px 16px;
    border-radius: 12px;
    background: @theme_base_color;
    border: 1px solid alpha(@theme_fg_color, 0.08);
    box-shadow: none;
}

/* ── Preferences window ── */
/* ── Preferences window ── */
.prefs-root {
    background: @theme_bg_color;
}

.prefs-header {
    padding: 4px 8px;
    background: @theme_bg_color;
    border-bottom: 1px solid alpha(@theme_fg_color, 0.10);
    box-shadow: none;
    color: @theme_fg_color;
}

.prefs-tabs-group {
    background: alpha(@theme_fg_color, 0.10);
    border-radius: 9px;
    padding: 3px;
}

.prefs-tab {
    border-radius: 7px;
    padding: 3px 16px;
    background: transparent;
    border: none;
    font-weight: 500;
    font-size: 13px;
    min-height: 26px;
    box-shadow: none;
    color: @theme_fg_color;
}

.prefs-tab:hover {
    background: transparent;
}

.prefs-tab:checked {
    background: @theme_base_color;
    color: @theme_fg_color;
    box-shadow: none;
}

.prefs-scroll {
    margin: 2px 16px 20px 16px;
}

.prefs-section-title {
    font-weight: 400;
    font-size: 11px;
    color: alpha(@theme_fg_color, 0.65);
    margin: 14px 0 5px 8px;
    letter-spacing: 0.4px;
}

.prefs-card {
    border-radius: 12px;
    background: @theme_base_color;
    border: 1px solid alpha(@theme_fg_color, 0.08);
    box-shadow: none;
}

.prefs-row {
    min-height: 40px;
    padding: 6px 14px;
}

.prefs-row-title {
    font-size: 14px;
    font-weight: 400;
}

.prefs-row-subtitle {
    font-size: 12px;
    color: alpha(@theme_fg_color, 0.70);
}

.prefs-row-value {
    font-size: 14px;
    color: alpha(@theme_fg_color, 0.78);
}

/* Apple-style compact switch */
.prefs-row switch {
    min-width: 34px;
    min-height: 20px;
    border-radius: 10px;
    background: alpha(@theme_fg_color, 0.20);
    border: none;
    padding: 0;
    margin: 0;
    transition: background 200ms ease;
}

.prefs-row switch:checked {
    background: #0a84ff;
}

.prefs-row switch slider {
    min-width: 16px;
    min-height: 16px;
    border-radius: 8px;
    background: @theme_base_color;
    border: none;
    box-shadow: 0 1px 2px alpha(@theme_fg_color, 0.22);
    margin: 2px;
    transition: margin 200ms ease;
}

/* Flat inline dropdown */
.prefs-row dropdown {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    min-height: 0;
}

.prefs-row dropdown button {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0 2px;
    font-size: 14px;
    color: @theme_fg_color;
}

.prefs-row dropdown button:hover {
    background: transparent;
}

.prefs-row dropdown button arrow {
    color: alpha(@theme_fg_color, 0.70);
    -gtk-icon-size: 12px;
}

.prefs-flat-button {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0 2px;
    min-height: 0;
    color: @theme_fg_color;
}

.prefs-flat-button:hover {
    background: transparent;
}
"""

SECRET_SCHEMA = Secret.Schema.new(
    APP_ID,
    Secret.SchemaFlags.NONE,
    {'service': Secret.SchemaAttributeType.STRING},
)
SECRET_ATTRS = {'service': 'lunday-credentials'}


def load_credentials():
    raw = Secret.password_lookup_sync(SECRET_SCHEMA, SECRET_ATTRS, None)
    if raw:
        try:
            return json.loads(raw)
        except (ValueError, KeyError):
            pass
    return None


def save_credentials(email, password):
    Secret.password_store_sync(
        SECRET_SCHEMA, SECRET_ATTRS,
        Secret.COLLECTION_DEFAULT,
        'Lunday login credentials',
        json.dumps({'email': email, 'password': password}),
        None,
    )


AUTO_FILL_JS = """
(function tryFill(attempts) {{
    const email = {email_json};
    const password = {password_json};

    function fill(selector, value) {{
        const el = document.querySelector(selector);
        if (!el) return false;
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeSetter.call(el, value);
        el.dispatchEvent(new Event('input', {{bubbles: true}}));
        el.dispatchEvent(new Event('change', {{bubbles: true}}));
        return true;
    }}

    const filledEmail    = fill('input[type="email"], input[name="email"], input[autocomplete="email"]', email);
    const filledPassword = fill('input[type="password"]', password);

    if (filledEmail && filledPassword) {{
        const btn = document.querySelector('button[type="submit"], button[data-testid*="login"], button[class*="login"]');
        if (btn) btn.click();
    }} else if (attempts > 0) {{
        setTimeout(() => tryFill(attempts - 1), 600);
    }}
}})(20);
"""

NOTIFICATION_BRIDGE_JS = """
(function() {
    if (window.__lundayNativeNotifyInstalled) { return; }
    window.__lundayNativeNotifyInstalled = true;

    function extractBody(options) {
        if (!options) return '';
        // Standard body field
        if (options.body) return String(options.body);
        // Some apps put the message in data
        if (options.data) {
            if (typeof options.data === 'string') return options.data;
            if (typeof options.data === 'object') {
                const d = options.data;
                return String(d.body || d.message || d.text || d.content || '');
            }
        }
        return '';
    }

    function postNative(title, body) {
        try {
            if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nativeNotify) {
                window.webkit.messageHandlers.nativeNotify.postMessage(
                    JSON.stringify({ title: String(title || 'Lunday'), body: String(body || '') })
                );
            }
        } catch (e) {}
    }

    /* ── Override window.Notification ── */
    const OrigNotification = window.Notification;
    function PatchedNotification(title, options) {
        postNative(title, extractBody(options));
        if (OrigNotification) {
            try { return new OrigNotification(title, options); } catch(e) {}
        }
    }
    if (OrigNotification && OrigNotification.prototype) {
        PatchedNotification.prototype = OrigNotification.prototype;
    }
    PatchedNotification.requestPermission = function(cb) {
        if (typeof cb === 'function') try { cb('granted'); } catch(e) {}
        return Promise.resolve('granted');
    };
    try {
        Object.defineProperty(PatchedNotification, 'permission', { get: function(){ return 'granted'; }, configurable: true });
    } catch(e) { PatchedNotification.permission = 'granted'; }
    window.Notification = PatchedNotification;

    /* ── Intercept ServiceWorkerRegistration.showNotification ── */
    if (window.ServiceWorkerRegistration && ServiceWorkerRegistration.prototype.showNotification) {
        const origShow = ServiceWorkerRegistration.prototype.showNotification;
        ServiceWorkerRegistration.prototype.showNotification = function(title, options) {
            postNative(title, extractBody(options));
            return origShow.call(this, title, options);
        };
    }
})();
"""


class LundayApplication(Gtk.Application):
    def __init__(self, flags=Gio.ApplicationFlags.FLAGS_NONE):
        super().__init__(application_id=APP_ID, flags=flags)
        self._credentials = None
        self._webview = None
        self._session = None
        self._zoom_level = 1.0
        self._last_workspace_url = None
        self._window_width = 1280
        self._window_height = 800
        self._notification_sound_enabled = True
        self._prefs_path = None
        self._workspace_subtitle = None
        self._loading_label = None
        self._nav_reload_btn = None
        self._preferences_window = None
        self._about_window = None
        self._css_provider = None
        self._notification_sound_name = DEFAULT_NOTIFICATION_SOUND_NAME
        self._notification_sound_custom_path = None  # path to user-chosen audio file
        self._theme_preference = 0  # 0=follow system, 1=light, 2=dark
        self._autostart_enabled = False
        self._run_in_background = False
        self._content_manager = None

        self._install_css()

        self._add_action('zoom-in', self._on_zoom_in)
        self._add_action('zoom-out', self._on_zoom_out)
        self._add_action('zoom-reset', self._on_zoom_reset)
        self._add_action('preferences', self._on_preferences)
        self._add_action('sign-out', self._on_sign_out)
        self._add_action('about', self._on_about)
        self._add_action('quit', self._on_quit)

        self.set_accels_for_action('app.zoom-in', ['<Ctrl>plus', '<Ctrl>equal'])
        self.set_accels_for_action('app.zoom-out', ['<Ctrl>minus'])
        self.set_accels_for_action('app.zoom-reset', ['<Ctrl>0'])

    def _add_action(self, name, callback):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)

    def _install_css(self):
        display = Gdk.Display.get_default()
        if display is not None:
            if self._css_provider is None:
                self._css_provider = Gtk.CssProvider()
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    self._css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
        if self._css_provider is not None:
            self._css_provider.load_from_data(APP_CSS)

    def _get_prefs_path(self):
        if self._prefs_path is None:
            data_dir = GLib.build_filenamev([GLib.get_user_data_dir(), 'lunday'])
            GLib.mkdir_with_parents(data_dir, 0o700)
            self._prefs_path = GLib.build_filenamev([data_dir, 'preferences.json'])
        return self._prefs_path

    def _store_custom_sound_file(self, source_file):
        data_dir = os.path.dirname(self._get_prefs_path())
        sounds_dir = GLib.build_filenamev([data_dir, 'sounds'])
        GLib.mkdir_with_parents(sounds_dir, 0o700)

        basename = source_file.get_basename() or 'custom-notify.wav'
        _name, ext = os.path.splitext(basename)
        if not ext:
            ext = '.wav'

        dest_path = GLib.build_filenamev([sounds_dir, f'custom-notify{ext.lower()}'])
        dest = Gio.File.new_for_path(dest_path)
        source_file.copy(dest, Gio.FileCopyFlags.OVERWRITE, None, None, None)
        return dest_path

    def _load_preferences(self):
        path = self._get_prefs_path()
        try:
            ok, content, _etag = Gio.File.new_for_path(path).load_contents(None)
            if ok:
                prefs = json.loads(content.decode('utf-8'))
                zoom = float(prefs.get('zoom_level', 1.0))
                self._zoom_level = max(0.8, min(2.0, zoom))
                last_url = prefs.get('last_workspace_url')
                if isinstance(last_url, str) and '.monday.com' in last_url:
                    self._last_workspace_url = last_url
                width = prefs.get('window_width')
                height = prefs.get('window_height')
                if isinstance(width, int) and isinstance(height, int):
                    if width >= 640 and height >= 480:
                        self._window_width = width
                        self._window_height = height
                self._notification_sound_enabled = bool(
                    prefs.get('notification_sound_enabled', True)
                )
                sound_name = prefs.get('notification_sound_name', DEFAULT_NOTIFICATION_SOUND_NAME)

                if sound_name == CUSTOM_NOTIFICATION_SOUND_NAME:
                    self._notification_sound_name = CUSTOM_NOTIFICATION_SOUND_NAME
                else:
                    # Backward-compat: map all legacy tone names to packaged default sound.
                    self._notification_sound_name = DEFAULT_NOTIFICATION_SOUND_NAME
                custom_path = prefs.get('notification_sound_custom_path')
                if isinstance(custom_path, str) and custom_path:
                    self._notification_sound_custom_path = custom_path
                    self._notification_sound_name = CUSTOM_NOTIFICATION_SOUND_NAME
                self._theme_preference = int(prefs.get('theme_preference', 0))
                self._autostart_enabled = bool(prefs.get('autostart_enabled', False))
                self._run_in_background = bool(prefs.get('run_in_background', False))
        except Exception:
            self._zoom_level = 1.0
            self._last_workspace_url = None
            self._window_width = 1280
            self._window_height = 800
            self._notification_sound_enabled = True
            self._notification_sound_name = DEFAULT_NOTIFICATION_SOUND_NAME
            self._notification_sound_custom_path = None
            self._theme_preference = 0
            self._autostart_enabled = False
            self._run_in_background = False

    def _save_preferences(self):
        path = self._get_prefs_path()
        prefs = {
            'zoom_level': self._zoom_level,
            'last_workspace_url': self._last_workspace_url,
            'window_width': self._window_width,
            'window_height': self._window_height,
            'notification_sound_enabled': self._notification_sound_enabled,
            'notification_sound_name': self._notification_sound_name,
            'notification_sound_custom_path': self._notification_sound_custom_path,
            'theme_preference': self._theme_preference,
            'autostart_enabled': self._autostart_enabled,
            'run_in_background': self._run_in_background,
        }
        try:
            Gio.File.new_for_path(path).replace_contents(
                json.dumps(prefs).encode('utf-8'),
                None,
                False,
                Gio.FileCreateFlags.REPLACE_DESTINATION,
                None,
            )
        except Exception:
            pass

    def _apply_autostart(self):
        """Write or remove an autostart .desktop entry."""
        autostart_dir = GLib.build_filenamev([GLib.get_user_config_dir(), 'autostart'])
        GLib.mkdir_with_parents(autostart_dir, 0o700)
        dest = GLib.build_filenamev([autostart_dir, f'{APP_ID}.desktop'])
        dest_file = Gio.File.new_for_path(dest)
        if self._autostart_enabled:
            desktop_content = (
                '[Desktop Entry]\n'
                'Type=Application\n'
                f'Name=Lunday\n'
                f'Exec=flatpak run {APP_ID}\n'
                'Icon=io.github.ulitus.Lunday\n'
                'X-GNOME-Autostart-enabled=true\n'
                'Comment=Start Lunday on login\n'
            )
            try:
                dest_file.replace_contents(
                    desktop_content.encode(),
                    None, False,
                    Gio.FileCreateFlags.REPLACE_DESTINATION,
                    None,
                )
            except Exception as exc:
                print(f'[autostart] write error: {exc}', file=sys.stderr)
        else:
            try:
                dest_file.delete(None)
            except Exception:
                pass

    def _apply_theme_preference(self):
        gtk_settings = Gtk.Settings.get_default()
        if gtk_settings is not None:
            if self._theme_preference == 1:
                gtk_settings.props.gtk_application_prefer_dark_theme = False
            elif self._theme_preference == 2:
                gtk_settings.props.gtk_application_prefer_dark_theme = True
            else:
                gtk_settings.reset_property('gtk-application-prefer-dark-theme')

        if self._webview is not None:
            settings = self._webview.get_settings()
            if settings is not None and hasattr(settings, 'set_preferred_color_scheme'):
                try:
                    if self._theme_preference == 1:
                        settings.set_preferred_color_scheme(WebKit.ColorScheme.LIGHT)
                    elif self._theme_preference == 2:
                        settings.set_preferred_color_scheme(WebKit.ColorScheme.DARK)
                    else:
                        settings.set_preferred_color_scheme(WebKit.ColorScheme.NO_PREFERENCE)
                except Exception:
                    pass

        # Reloading the single connected CSS provider triggers GTK's full CSS
        # invalidation pass so all @theme_* colors are re-resolved immediately.
        if self._css_provider is not None:
            self._css_provider.load_from_data(APP_CSS)
        display = Gdk.Display.get_default()
        if display is not None:
            try:
                Gtk.StyleContext.reset_widgets(display)
            except Exception:
                pass

    def _apply_zoom(self):
        if self._webview is not None:
            self._webview.set_zoom_level(self._zoom_level)

    def _change_zoom(self, delta):
        self._zoom_level = max(0.8, min(2.0, self._zoom_level + delta))
        self._apply_zoom()
        self._save_preferences()

    def _on_zoom_in(self, action, param):
        self._change_zoom(0.1)

    def _on_zoom_out(self, action, param):
        self._change_zoom(-0.1)

    def _on_zoom_reset(self, action, param):
        self._zoom_level = 1.0
        self._apply_zoom()
        self._save_preferences()

    def _on_sign_out(self, action, param):
        # Clear saved credentials from keyring
        try:
            Secret.password_clear_sync(SECRET_SCHEMA, SECRET_ATTRS, None)
        except Exception as exc:
            print(f'[sign-out] keyring clear error: {exc}', file=sys.stderr)
        self._credentials = None
        self._last_workspace_url = None
        self._save_preferences()

        if self._session is not None:
            data_manager = self._session.get_website_data_manager()
            if data_manager is not None:
                # Clear ALL WebKit-stored data: cookies, cache, localStorage,
                # IndexedDB, service workers, etc. — then navigate to login.
                data_manager.clear(
                    WebKit.WebsiteDataTypes.ALL,
                    0,
                    None,
                    self._on_sign_out_data_cleared,
                )
                return
            # Fallback: cookie-only clear
            self._session.get_cookie_manager().delete_all_cookies()

        if self._webview is not None:
            self._webview.load_uri(START_URL)

    def _on_sign_out_data_cleared(self, data_manager, result):
        try:
            data_manager.clear_finish(result)
        except Exception as exc:
            print(f'[sign-out] website data clear error: {exc}', file=sys.stderr)
        if self._webview is not None:
            self._webview.load_uri(START_URL)

    def _on_about(self, action, param):
        if self._about_window is not None:
            self._about_window.present()
            return

        parent = self.props.active_window
        window = Gtk.Window(title='About', transient_for=parent, modal=True)
        window.set_default_size(460, 360)
        window.set_resizable(False)

        header = Gtk.HeaderBar()
        header.add_css_class('prefs-header')
        header.set_show_title_buttons(True)
        title = Gtk.Label(label='About')
        title.add_css_class('workspace-title')
        header.set_title_widget(title)
        window.set_titlebar(header)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.add_css_class('prefs-root')
        root.set_vexpand(True)
        root.set_hexpand(True)

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=12,
            margin_bottom=12,
            margin_start=16,
            margin_end=16,
        )
        content.add_css_class('prefs-scroll')
        content.set_hexpand(True)
        content.set_valign(Gtk.Align.START)

        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hero.set_halign(Gtk.Align.CENTER)
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        if icon_theme is not None and icon_theme.has_icon(APP_ID):
            logo = Gtk.Image.new_from_icon_name(APP_ID)
        else:
            logo = Gtk.Image.new_from_icon_name('applications-office-symbolic')
        logo.set_pixel_size(72)
        app_name = Gtk.Label(label='Lunday')
        app_name.add_css_class('workspace-title')
        app_version = Gtk.Label(label=f'Version {APP_VERSION}')
        app_version.add_css_class('workspace-subtitle')
        hero.append(logo)
        hero.append(app_name)
        hero.append(app_version)
        content.append(hero)

        description = self._pref_make_row('Description', 'Unofficial Monday.com desktop app built with GTK and WebKit.')
        desc_col = description.get_first_child()
        if desc_col is not None:
            subtitle = desc_col.get_last_child()
            if subtitle is not None:
                subtitle.set_wrap(True)
                subtitle.set_max_width_chars(40)

        app_id_row = self._pref_make_row('Application ID', APP_ID)

        self._pref_add_section(content, 'APPLICATION', [
            description,
            app_id_row,
        ])

        self._pref_add_section(content, 'CREDITS', [
            self._pref_make_row('Design and Development', 'ulitus'),
        ])

        root.append(content)
        window.set_child(root)

        def on_close(_win):
            self._about_window = None
            return False

        window.connect('close-request', on_close)
        self._about_window = window
        window.present()

    def _pref_make_row(self, title, subtitle, right_widget=None):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class('prefs-row')

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        left.set_hexpand(True)
        left.set_halign(Gtk.Align.START)

        title_label = Gtk.Label(label=title, xalign=0)
        title_label.add_css_class('prefs-row-title')
        subtitle_label = Gtk.Label(label=subtitle, xalign=0)
        subtitle_label.add_css_class('prefs-row-subtitle')

        left.append(title_label)
        left.append(subtitle_label)
        row.append(left)

        if right_widget is not None:
            right_widget.set_valign(Gtk.Align.CENTER)
            row.append(right_widget)

        return row

    def _pref_make_value(self, text, chevron=True):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=text)
        label.add_css_class('prefs-row-value')
        box.append(label)
        if chevron:
            box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))
        return box

    def _pref_add_section(self, parent_box, title, rows):
        title_label = Gtk.Label(label=title, xalign=0)
        title_label.add_css_class('prefs-section-title')
        parent_box.append(title_label)

        card = Gtk.Frame()
        card.add_css_class('prefs-card')
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        for i, row in enumerate(rows):
            content.append(row)
            if i < len(rows) - 1:
                content.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        card.set_child(content)
        parent_box.append(card)

    def _build_general_tab(self):
        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=8,
            margin_bottom=16,
            margin_start=12,
            margin_end=12,
        )

        theme_items = Gtk.StringList.new(['Follow System', 'Light', 'Dark'])
        theme_dropdown = Gtk.DropDown.new(theme_items, None)
        theme_dropdown.set_selected(self._theme_preference)

        def on_theme_changed(dd, _param):
            idx = dd.get_selected()
            self._theme_preference = idx
            self._apply_theme_preference()
            self._save_preferences()

        theme_dropdown.connect('notify::selected', on_theme_changed)

        self._pref_add_section(root, 'APPEARANCE', [
            self._pref_make_row('Theme', 'Choose the application color scheme', theme_dropdown),
        ])

        autostart_switch = Gtk.Switch(active=self._autostart_enabled)

        def on_autostart_toggled(sw, _param):
            self._autostart_enabled = sw.get_active()
            self._apply_autostart()
            self._save_preferences()

        autostart_switch.connect('notify::active', on_autostart_toggled)

        background_switch = Gtk.Switch(active=self._run_in_background)

        def on_background_toggled(sw, _param):
            self._run_in_background = sw.get_active()
            self._save_preferences()

        background_switch.connect('notify::active', on_background_toggled)

        self._pref_add_section(root, 'STARTUP', [
            self._pref_make_row('Start with System', 'Launch automatically when you log in', autostart_switch),
            self._pref_make_row('Run in Background', 'Keep running when the window is closed', background_switch),
        ])

        return root

    def _build_accessibility_tab(self):
        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=8,
            margin_bottom=16,
            margin_start=12,
            margin_end=12,
        )

        zoom_value = Gtk.Label(label=f'{self._zoom_level:.1f}×')
        zoom_value.add_css_class('prefs-row-value')
        zoom_value.set_width_chars(5)
        zoom_value.set_xalign(0.5)

        zoom_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        minus_btn = Gtk.Button(label='−')
        plus_btn = Gtk.Button(label='+')
        minus_btn.add_css_class('prefs-flat-button')
        plus_btn.add_css_class('prefs-flat-button')

        def on_zoom_minus(*_args):
            self._change_zoom(-0.1)
            zoom_value.set_label(f'{self._zoom_level:.1f}×')

        def on_zoom_plus(*_args):
            self._change_zoom(0.1)
            zoom_value.set_label(f'{self._zoom_level:.1f}×')

        minus_btn.connect('clicked', on_zoom_minus)
        plus_btn.connect('clicked', on_zoom_plus)
        zoom_controls.append(minus_btn)
        zoom_controls.append(zoom_value)
        zoom_controls.append(plus_btn)

        reset_btn = Gtk.Button(label='Reset')
        reset_btn.add_css_class('prefs-flat-button')
        reset_btn.connect('clicked', lambda *_args: (
            self._on_zoom_reset(None, None),
            zoom_value.set_label(f'{self._zoom_level:.1f}×'),
        ))

        self._pref_add_section(root, 'ZOOM', [
            self._pref_make_row('Zoom Level', 'Current zoom level for the web view', zoom_controls),
            self._pref_make_row('Reset Zoom', 'Restore to 100%', reset_btn),
        ])

        return root

    def _build_notification_tab(self):
        root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=8,
            margin_bottom=16,
            margin_start=12,
            margin_end=12,
        )

        sound_switch = Gtk.Switch(active=self._notification_sound_enabled)
        sound_switch.connect('notify::active', self._on_notification_sound_toggled)

        # Dropdown: packaged default + custom file option
        all_sound_names = [DEFAULT_NOTIFICATION_SOUND_NAME, 'Custom File…']
        sound_items = Gtk.StringList.new(all_sound_names)
        sound_dropdown = Gtk.DropDown.new(sound_items, None)

        if self._notification_sound_name == CUSTOM_NOTIFICATION_SOUND_NAME:
            current_idx = len(all_sound_names) - 1
        else:
            current_idx = 0
        sound_dropdown.set_selected(current_idx)

        state = {'internal_change': False}

        def open_custom_sound_dialog():
            dialog = Gtk.FileDialog()
            dialog.set_title('Choose notification sound')
            f = Gio.File.new_for_path(self._notification_sound_custom_path) if self._notification_sound_custom_path else None
            if f:
                dialog.set_initial_file(f)
            filter_audio = Gtk.FileFilter()
            filter_audio.set_name('Audio files')
            for pat in ['*.mp3', '*.ogg', '*.oga', '*.wav', '*.flac', '*.m4a', '*.opus']:
                filter_audio.add_pattern(pat)
            filters = Gio.ListStore.new(Gtk.FileFilter)
            filters.append(filter_audio)
            dialog.set_filters(filters)
            parent = self._preferences_window
            dialog.open(parent, None, on_file_chosen)

        def on_file_chosen(dialog, result):
            try:
                f = dialog.open_finish(result)
                if f is not None:
                    stored_path = self._store_custom_sound_file(f)
                    if stored_path:
                        self._notification_sound_custom_path = stored_path
                        self._notification_sound_name = CUSTOM_NOTIFICATION_SOUND_NAME
                        self._save_preferences()
                        if self._notification_sound_enabled:
                            self._play_notification_sound()
            except Exception:
                # If user cancels without an existing custom sound, keep Default selected.
                if not self._notification_sound_custom_path:
                    self._notification_sound_name = DEFAULT_NOTIFICATION_SOUND_NAME
                    state['internal_change'] = True
                    sound_dropdown.set_selected(0)
                    state['internal_change'] = False
                    self._save_preferences()

        def on_sound_changed(dd, _param):
            if state['internal_change']:
                return
            idx = dd.get_selected()
            if idx == len(all_sound_names) - 1:
                # Custom File selected: open picker immediately.
                open_custom_sound_dialog()
            elif idx == 0:
                self._notification_sound_name = DEFAULT_NOTIFICATION_SOUND_NAME
                self._notification_sound_custom_path = None
                self._save_preferences()
                if self._notification_sound_enabled:
                    self._play_notification_sound()

        sound_dropdown.connect('notify::selected', on_sound_changed)

        self._pref_add_section(root, 'SOUNDS', [
            self._pref_make_row('Notification Sounds', 'Play a sound when a notification arrives', sound_switch),
            self._pref_make_row('Sound', 'Choose the notification alert sound', sound_dropdown),
        ])

        return root

    def _on_preferences(self, action, param):
        if self._preferences_window is not None:
            self._preferences_window.present()
            return

        parent = self.props.active_window
        window = Gtk.Window(title='Preferences', transient_for=parent, modal=True)
        window.set_default_size(580, 560)
        window.set_resizable(False)

        # --- Header bar with segmented tab control ---
        header = Gtk.HeaderBar()
        header.add_css_class('prefs-header')
        header.set_show_title_buttons(True)

        tabs_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        tabs_group.add_css_class('prefs-tabs-group')

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_vexpand(True)
        stack.set_hexpand(True)

        general_scroll = Gtk.ScrolledWindow()
        general_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        general_scroll.set_child(self._build_general_tab())
        general_scroll.add_css_class('prefs-scroll')

        accessibility_scroll = Gtk.ScrolledWindow()
        accessibility_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        accessibility_scroll.set_child(self._build_accessibility_tab())
        accessibility_scroll.add_css_class('prefs-scroll')

        notifications_scroll = Gtk.ScrolledWindow()
        notifications_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        notifications_scroll.set_child(self._build_notification_tab())
        notifications_scroll.add_css_class('prefs-scroll')

        stack.add_named(general_scroll, 'general')
        stack.add_named(accessibility_scroll, 'accessibility')
        stack.add_named(notifications_scroll, 'notifications')

        tab_general = Gtk.ToggleButton(label='General')
        tab_general.add_css_class('prefs-tab')
        tab_accessibility = Gtk.ToggleButton(label='Accessibility')
        tab_accessibility.add_css_class('prefs-tab')
        tab_notifications = Gtk.ToggleButton(label='Notifications')
        tab_notifications.add_css_class('prefs-tab')

        tabs = {
            'general': tab_general,
            'accessibility': tab_accessibility,
            'notifications': tab_notifications,
        }

        def select_tab(name):
            stack.set_visible_child_name(name)
            for key, button in tabs.items():
                button.set_active(key == name)

        tab_general.connect('clicked', lambda *_: select_tab('general'))
        tab_accessibility.connect('clicked', lambda *_: select_tab('accessibility'))
        tab_notifications.connect('clicked', lambda *_: select_tab('notifications'))

        tabs_group.append(tab_general)
        tabs_group.append(tab_accessibility)
        tabs_group.append(tab_notifications)
        header.set_title_widget(tabs_group)
        window.set_titlebar(header)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.add_css_class('prefs-root')
        root.set_vexpand(True)
        root.set_hexpand(True)
        root.append(stack)

        select_tab('general')
        window.set_child(root)

        def on_close(_win):
            self._preferences_window = None
            return False

        window.connect('close-request', on_close)
        self._preferences_window = window
        window.present()

    def _on_notification_sound_toggled(self, switch, _param):
        self._notification_sound_enabled = switch.get_active()
        self._save_preferences()

    def _on_quit(self, action, param):
        self.quit()

    def _on_reload_clicked(self, button):
        if self._webview is not None:
            self._webview.reload()

    def _set_loading_state(self, loading):
        if self._loading_label is not None:
            self._loading_label.set_visible(loading)
            self._loading_label.set_label('Loading...' if loading else '')

    def _update_workspace_subtitle(self, uri):
        if self._workspace_subtitle is None:
            return
        host = urlparse(uri).netloc if uri else ''
        self._workspace_subtitle.set_label(host or 'Loading...')

    def _update_nav_buttons(self):
        if self._nav_reload_btn is not None:
            self._nav_reload_btn.set_sensitive(self._webview is not None)

    def _on_window_close_request(self, window):
        width = window.get_width()
        height = window.get_height()
        if width >= 640 and height >= 480:
            self._window_width = width
            self._window_height = height
            self._save_preferences()
        if self._run_in_background:
            window.hide()
            return True  # prevent destroy — app keeps running in background
        return False

    def do_activate(self):
        window = self.props.active_window
        if window is None:
            window = Gtk.ApplicationWindow(application=self)
            window.set_title('Lunday')

            self._load_preferences()
            window.set_default_size(self._window_width, self._window_height)
            window.connect('close-request', self._on_window_close_request)

            header = Gtk.HeaderBar()
            header.add_css_class('modern-header')
            menu_model = Gio.Menu.new()
            menu_model.append('Preferences', 'app.preferences')
            menu_model.append('Sign out', 'app.sign-out')
            menu_model.append('About', 'app.about')
            menu_model.append('Quit', 'app.quit')

            app_menu_btn = Gtk.MenuButton(icon_name='open-menu-symbolic')
            app_menu_btn.add_css_class('menu-button')
            app_menu_btn.set_tooltip_text('Menu')
            app_menu_btn.set_popover(Gtk.PopoverMenu.new_from_model(menu_model))
            header.pack_start(app_menu_btn)

            self._nav_reload_btn = Gtk.Button(icon_name='view-refresh-symbolic')
            self._nav_reload_btn.add_css_class('nav-button')
            self._nav_reload_btn.set_tooltip_text('Reload')
            self._nav_reload_btn.connect('clicked', self._on_reload_clicked)
            header.pack_start(self._nav_reload_btn)

            title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            title_box.set_valign(Gtk.Align.CENTER)
            title_label = Gtk.Label(label='Lunday')
            title_label.add_css_class('workspace-title')
            title_label.set_halign(Gtk.Align.CENTER)
            self._workspace_subtitle = Gtk.Label(label='Loading...')
            self._workspace_subtitle.add_css_class('workspace-subtitle')
            self._workspace_subtitle.set_halign(Gtk.Align.CENTER)
            self._loading_label = Gtk.Label(label='')
            self._loading_label.add_css_class('loading-text')
            self._loading_label.set_halign(Gtk.Align.CENTER)
            self._loading_label.set_visible(False)
            title_box.append(title_label)
            title_box.append(self._workspace_subtitle)
            title_box.append(self._loading_label)
            header.set_title_widget(title_box)
            window.set_titlebar(header)

            data_dir = GLib.build_filenamev([GLib.get_user_data_dir(), 'monday'])
            GLib.mkdir_with_parents(data_dir, 0o700)
            cookie_path = GLib.build_filenamev([data_dir, 'cookies.sqlite'])

            session = WebKit.NetworkSession.get_default()
            self._session = session
            session.get_cookie_manager().set_persistent_storage(
                cookie_path,
                WebKit.CookiePersistentStorage.SQLITE,
            )

            self._content_manager = WebKit.UserContentManager()
            try:
                self._content_manager.register_script_message_handler('nativeNotify')
                self._content_manager.connect(
                    'script-message-received::nativeNotify',
                    self._on_native_notify_message,
                )
                # Inject bridge as UserScript so it runs at document-start, before
                # Monday's own JS registers service workers / notification handlers.
                bridge_script = WebKit.UserScript.new(
                    NOTIFICATION_BRIDGE_JS,
                    WebKit.UserContentInjectedFrames.ALL_FRAMES,
                    WebKit.UserScriptInjectionTime.START,
                    ['https://*.monday.com/*'],
                    None,
                )
                self._content_manager.add_script(bridge_script)
            except Exception as exc:
                print(f'[bridge] setup error: {exc}', file=sys.stderr)
                self._content_manager = None

            if self._content_manager is not None:
                webview = WebKit.WebView(
                    network_session=session,
                    user_content_manager=self._content_manager,
                )
            else:
                webview = WebKit.WebView(network_session=session)

            self._webview = webview
            settings = webview.get_settings()
            if settings is not None:
                try:
                    settings.set_enable_web_notifications(True)
                except Exception:
                    pass
                try:
                    settings.set_enable_notifications(True)
                except Exception:
                    pass
            self._apply_theme_preference()
            self._apply_zoom()
            webview.connect('load-changed', self._on_load_changed)
            webview.connect('permission-request', self._on_permission_request)
            webview.connect('show-notification', self._on_show_notification)
            webview.connect('notify::uri', lambda *_args: self._update_workspace_subtitle(webview.get_uri() or ''))
            webview.load_uri(self._last_workspace_url or START_URL)

            card = Gtk.Frame()
            card.add_css_class('content-card')
            card.set_child(webview)

            window.set_child(card)
            window.present()
            self._set_loading_state(True)
            self._update_nav_buttons()

            self._credentials = load_credentials()
        else:
            window.present()

    def _on_permission_request(self, webview, request):
        # Runtime/class names can differ across WebKitGTK versions.
        try:
            if isinstance(request, WebKit.NotificationPermissionRequest):
                request.allow()
                return True
        except Exception:
            pass

        gtype_name = request.__gtype__.name if hasattr(request, '__gtype__') else ''
        if 'NotificationPermissionRequest' in gtype_name and hasattr(request, 'allow'):
            request.allow()
            return True
        return False

    def _send_native_notification(self, title, body=''):
        notif = Gio.Notification.new(title or 'Lunday')
        if body:
            notif.set_body(body)
        notif.set_icon(Gio.ThemedIcon.new(APP_ID))
        if self._notification_sound_enabled:
            self._play_notification_sound()
        # Use a unique ID so notification daemon never deduplicates/collapses notifications
        notif_id = f'lunday-{GLib.get_monotonic_time()}'
        self.send_notification(notif_id, notif)

    def _on_native_notify_message(self, _manager, js_result):
        title = 'Lunday'
        body = ''
        try:
            # In WebKit 6, script-message-received passes a JSC.Value directly
            if hasattr(js_result, 'get_js_value'):
                jsc_value = js_result.get_js_value()
            else:
                jsc_value = js_result
            raw = jsc_value.to_string()
            print(f'[notify bridge] raw payload: {raw!r}', file=sys.stderr)
            data = json.loads(raw)
            title = str(data.get('title') or 'Lunday')
            body = str(data.get('body') or '')
        except Exception as exc:
            print(f'[notify bridge] parse error: {exc}', file=sys.stderr)
        self._send_native_notification(title, body)

    def _on_show_notification(self, webview, notification):
        title = notification.get_title() or 'Lunday'
        body = notification.get_body() or ''
        print(f'[show-notification] title={title!r} body={body!r}', file=sys.stderr)
        self._send_native_notification(title, body)
        return True  # prevent default (no-op) handling

    def _play_notification_sound(self):
        pipeline_str = None
        if self._notification_sound_name == CUSTOM_NOTIFICATION_SOUND_NAME and self._notification_sound_custom_path:
            safe_path = self._notification_sound_custom_path.replace('"', '\\"')
            pipeline_str = f'filesrc location="{safe_path}" ! decodebin ! audioconvert ! audioresample ! pulsesink'
        else:
            pipeline_str = (
                f'filesrc location="{DEFAULT_NOTIFICATION_SOUND_PATH}" '
                '! decodebin ! audioconvert ! audioresample ! pulsesink'
            )
        if pipeline_str is None:
            pipeline_str = (
                f'filesrc location="{DEFAULT_NOTIFICATION_SOUND_PATH}" '
                '! decodebin ! audioconvert ! audioresample ! pulsesink'
            )
        try:
            pipeline = Gst.parse_launch(pipeline_str)
            pipeline.set_state(Gst.State.PLAYING)

            def _on_message(bus, msg, pipe):
                if msg.type in (Gst.MessageType.EOS, Gst.MessageType.ERROR):
                    pipe.set_state(Gst.State.NULL)
                return True

            bus = pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect('message', _on_message, pipeline)
        except Exception as exc:
            print(f'[sound] GStreamer error: {exc}', file=sys.stderr)
            try:
                display = Gdk.Display.get_default()
                if display is not None:
                    display.beep()
            except Exception:
                pass

    def _on_load_changed(self, webview, event):
        if event in (WebKit.LoadEvent.STARTED, WebKit.LoadEvent.REDIRECTED, WebKit.LoadEvent.COMMITTED):
            self._set_loading_state(True)
            self._update_workspace_subtitle(webview.get_uri() or '')

        if event != WebKit.LoadEvent.FINISHED:
            self._update_nav_buttons()
            return

        self._set_loading_state(False)
        self._update_nav_buttons()
        uri = webview.get_uri() or ''
        if 'monday.com' not in uri:
            return

        if '.monday.com' in uri and 'auth.monday.com' not in uri and '/logout' not in uri:
            if uri != self._last_workspace_url:
                self._last_workspace_url = uri
                self._save_preferences()

        # Only auto-fill credentials on login/auth pages
        if not any(p in uri for p in ('/login', '/auth', 'auth.monday.com')):
            return
        creds = self._credentials
        if not creds:
            return
        js = AUTO_FILL_JS.format(
            email_json=json.dumps(creds['email']),
            password_json=json.dumps(creds['password']),
        )
        webview.evaluate_javascript(js, -1, None, None, None, None, None)


if __name__ == '__main__':
    app = LundayApplication()
    exit_code = app.run(None)

    # Some sessions may not expose the expected DBus services for unique-app
    # registration. Retry in NON_UNIQUE mode so the window can still open.
    if exit_code != 0:
        print('[startup] Retrying in NON_UNIQUE mode', file=sys.stderr)
        fallback_app = LundayApplication(flags=Gio.ApplicationFlags.NON_UNIQUE)
        exit_code = fallback_app.run(None)

    sys.exit(exit_code)
