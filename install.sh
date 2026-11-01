#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EFFECTS_DIR="$HOME/.local/share/kwin/effects"
SCRIPTS_DIR="$HOME/.local/share/kwin/scripts"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "==> Instalando efecto GNOME Overview..."
mkdir -p "$EFFECTS_DIR"
rm -rf "$EFFECTS_DIR/gnomeoverview"
cp -r "$SCRIPT_DIR/gnomeoverview" "$EFFECTS_DIR/"

# Asignar tecla Meta a GNOME Overview en kglobalshortcutsrc
echo "==> Configurando tecla Meta (Super) para GNOME Overview..."
python3 -c '
import os
path = os.path.expanduser("~/.config/kglobalshortcutsrc")
if os.path.exists(path):
    with open(path, "r") as f:
        lines = f.readlines()

    new_lines = []
    has_gnome_overview = False
    for line in lines:
        if line.startswith("Overview="):
            new_lines.append("Overview=none,none,Conmutar a la vista general\\n")
        elif line.startswith("GNOME Overview="):
            new_lines.append("GNOME Overview=Meta\\tMeta+W,none,Toggle GNOME Overview\\n")
            has_gnome_overview = True
        else:
            new_lines.append(line)

    if not has_gnome_overview:
        new_lines.append("GNOME Overview=Meta\\tMeta+W,none,Toggle GNOME Overview\\n")

    with open(path, "w") as f:
        f.writelines(new_lines)
'

# Habilitar script oficial de KWin para escritorios virtuales solo en pantalla principal por defecto
echo "==> Configurando escritorios virtuales solo en pantalla principal por defecto..."
(flatpak-spawn --host kwriteconfig6 --file kwinrc --group Plugins --key virtualdesktopsonlyonprimaryEnabled "true" || kwriteconfig6 --file kwinrc --group Plugins --key virtualdesktopsonlyonprimaryEnabled "true") 2>/dev/null || true
(flatpak-spawn --host kwriteconfig6 --file kwinrc --group Effect-gnomeoverview --key DesktopsOnlyOnPrimary "true" || kwriteconfig6 --file kwinrc --group Effect-gnomeoverview --key DesktopsOnlyOnPrimary "true") 2>/dev/null || true

# Configurar servicio gnome-meta-scroll (Meta + rueda en cualquier lugar)
echo "==> Configurando servicio gnome-meta-scroll (Meta + rueda en cualquier lugar)..."
mkdir -p "$SYSTEMD_USER_DIR"
cat > "$SYSTEMD_USER_DIR/gnome-meta-scroll.service" <<SERVICE_EOF
[Unit]
Description=GNOME-style Meta + Mouse Wheel virtual desktop switcher
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $SCRIPT_DIR/gnome-meta-scroll/gnome_meta_scroll.py
Restart=always
RestartSec=3

[Install]
WantedBy=graphical-session.target
SERVICE_EOF

(flatpak-spawn --host systemctl --user daemon-reload || systemctl --user daemon-reload) 2>/dev/null || true
(flatpak-spawn --host systemctl --user enable --now gnome-meta-scroll.service || systemctl --user enable --now gnome-meta-scroll.service) 2>/dev/null || true

# Recargar configuración de KWin
echo "==> Recargando KWin..."
(flatpak-spawn --host qdbus6 org.kde.KWin /KWin reconfigure || qdbus6 org.kde.KWin /KWin reconfigure) 2>/dev/null || true

echo "==> ¡Listo! GNOME Overview y Meta + Scroll global están activos y funcionando."
