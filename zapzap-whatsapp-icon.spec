Name:           zapzap-whatsapp-icon
Version:        1.5
Release:        1%{?dist}
Summary:        Monochrome WhatsApp tray icon for ZapZap, with a discreet unread counter

License:        MIT
URL:            https://github.com/henriquecarmine/zapzap-whatsapp-icon
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       bash
Requires:       flatpak
Requires:       python3

%description
ZapZap ships a symbolic tray icon, but it draws the project's own "Z" mark and
its unread counter is a red pill in every theme. On a tray where everything
else is monochrome, that red blob is the one thing the eye keeps catching.

This replaces both, at runtime, for the SYMBOLIC themes only: the WhatsApp
mark instead of the "Z", and the counter as a digit in the same colour as the
glyph, with a gap opened behind it rather than a coloured badge. The 'default'
theme is left exactly as ZapZap made it — a patch that hijacks the user's
choice is a rude patch.

Nothing is written inside the flatpak, which is read-only and keeps updating
from Flathub as usual. A `flatpak override` points the application's
PYTHONPATH at a hook that patches the icon while it runs.

After installing, run:

    zapzap-whatsapp-icon --ativar

and pick a symbolic icon in ZapZap under Settings, Appearance. To undo:

    zapzap-whatsapp-icon --desativar

%prep
%setup -q

%install
install -d %{buildroot}%{_datadir}/%{name}/arte
install -d %{buildroot}%{_bindir}
install -m 0644 sitecustomize.py %{buildroot}%{_datadir}/%{name}/
install -m 0644 arte/*.svg       %{buildroot}%{_datadir}/%{name}/arte/
install -m 0644 gerar.py         %{buildroot}%{_datadir}/%{name}/
install -m 0755 zapzap-whatsapp-icon %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%{_datadir}/%{name}/
%{_bindir}/%{name}

%post
# Deliberately does NOT enable itself. Installing a package should not
# silently change how an application already on the machine looks; the user
# runs `--ativar` when they want it.
:

%preun
# On removal, take the override away — otherwise ZapZap keeps a PYTHONPATH
# pointing at files that no longer exist, and its icon quietly falls back
# with a warning on stderr nobody reads. $1 == 0 means uninstall, not upgrade.
if [ "$1" = "0" ]; then
    for lar in /home/*; do
        [ -d "$lar" ] || continue
        cfg="$lar/.local/share/flatpak/overrides/com.rtosta.zapzap"
        [ -f "$cfg" ] || continue
        grep -q "%{_datadir}/%{name}" "$cfg" 2>/dev/null && \
            sed -i "\|%{_datadir}/%{name}|d; /^PYTHONPATH=/d" "$cfg" || :
    done
fi
:

%changelog
* Sun Aug 16 2026 Henrique Carmine <henriquecarmine@gmail.com> - 1.5-1
- --ativar now installs the application icon too, one variant per theme:
  light for breeze-dark, dark for breeze, mid grey in hicolor as fallback.
  An application icon is NOT tinted by the theme — it renders in whatever
  colour the file carries — so a single currentColor version came out
  invisible on a dark panel.
- The variants go in directories the theme's index DECLARES. Breeze does not
  declare apps/scalable, and a file in an undeclared directory is ignored in
  silence; apps/48 is Type=Scalable Min=48 Max=256 and takes an SVG.
- --desativar removes them again.
- TrayIcon.getIcon() called with no argument now follows the user's chosen
  theme instead of defaulting to green. Three call sites did that: the window
  icon, notifications, and the icon renderer.

* Sun Aug 16 2026 Henrique Carmine <henriquecarmine@gmail.com> - 1.4-1
- Notifications follow the chosen tray theme too. IconRenderer.default_icon
  called TrayIcon.getIcon() with no argument, so it always got the green
  default regardless of what the user had picked.
- Also ships an application-icon override for the user's icon theme, so the
  small logo beside the notification title and in the launcher stops being
  the only coloured thing on screen. Remove the file to undo.

* Sun Aug 16 2026 Henrique Carmine <henriquecarmine@gmail.com> - 1.3-1
- The mark no longer fills the whole frame. Measured the ink of the
  neighbouring tray icons on a real panel: all 18 px tall, while this one
  came out at 22. Symbolic icons carry built-in margin; filling the frame
  made the mark stand out of the row.

* Sun Aug 16 2026 Henrique Carmine <henriquecarmine@gmail.com> - 1.2-1
- The mark is now the canonical WhatsApp geometry: an OUTLINED bubble with a
  filled handset. The previous drawing was the negative of that — a filled
  bubble with the handset knocked out — and the handset was too narrow.
  Checked against the authentic favicons pulled from WhatsApp Web's own cache
  inside ZapZap.
- With a counter, the mark shrinks and yields the bottom-right corner to the
  digit. Swapping the geometry broke the badge: a filled mark has solid area
  for the gap to punch, an outlined one does not, and the gap was destroying
  the outline instead of clearing space.

* Sun Aug 16 2026 Henrique Carmine <henriquecarmine@gmail.com> - 1.1-1
- Fix: the hook is now copied into the user's home before being pointed at.
  Flatpak REFUSES to share /usr with the sandbox ("the path /usr is reserved
  by Flatpak"), so pointing PYTHONPATH at the packaged copy left the hook
  unreachable and the patch failed silently — ZapZap opened with its original
  icon and nothing explained why. Caught by rendering the icon after a real
  install instead of trusting that the package layout would work.

* Sun Aug 16 2026 Henrique Carmine <henriquecarmine@gmail.com> - 1.0-1
- First release.
- WhatsApp mark, monochrome, replacing ZapZap's "Z" in symbolic themes.
- Unread counter as a digit in the glyph's colour with a gap opened behind
  it, instead of a red pill. Capped at 9+: rendered at 22 px and looked at,
  three digits are a smudge and the gap eats half the bubble.
- Applied through a PYTHONPATH hook and a flatpak override; nothing is
  written inside the read-only flatpak.
- The hook chains to the runtime's own sitecustomize. Without that, shadowing
  it dropped /app/lib/python3.13/site-packages from sys.path and PyQt6 failed
  to import — the application would not start.
