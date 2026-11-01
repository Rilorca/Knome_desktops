# Knome Desktops

Una experiencia fiel al flujo de trabajo de **GNOME Shell Workspaces** integrada nativamente en **KDE Plasma 6 (Wayland)**.

![KDE Plasma 6](https://img.shields.io/badge/KDE-Plasma%206-blue?logo=kde)
![Wayland](https://img.shields.io/badge/Display-Wayland-brightgreen)
![License](https://img.shields.io/badge/License-GPLv2-blue.svg)

---

## ✨ Características

- 🔍 **GNOME Overview con KRunner nativo**:
  - Tira superior horizontal de escritorios virtuales al estilo GNOME 40+.
  - Búsqueda integrada completa con Milou/KRunner (abre aplicaciones, busca archivos, calcula operaciones y ejecuta comandos directamente).
  - Activación con solo presionar la tecla **Meta (Super)** o `Meta + W`.
- 🔄 **Navegación con Rueda del Mouse (GNOME-style)**:
  - **En el Overview**: Gira la rueda del mouse en cualquier parte de la vista general para alternar entre escritorios virtuales.
  - **Global (`Meta + Rueda`)**: Mantén presionada la tecla `Meta` y gira la rueda del mouse en cualquier ventana o espacio libre para cambiar de escritorio virtual inmediatamente. Soporta ruedas normales y ruedas de alta resolución (Logitech MagSpeed, MX Master, etc.).
- 🖥️ **Escritorios virtuales solo en pantalla principal (Multi-monitor perfeccionado)**:
  - Por defecto, los escritorios virtuales solo existen y cambian en el monitor principal.
  - Las pantallas secundarias permanecen estáticas y no se desplazan ni duplican escritorios al navegar.

---

## 🚀 Instalación rápida

### Opción 1: Un solo comando (Recomendado)

Copia y pega la siguiente línea en tu terminal:

```bash
git clone https://github.com/Rilorca/Knome_desktops.git && cd Knome_desktops && ./install.sh
```

---

### Opción 2: Paso a paso

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/Rilorca/Knome_desktops.git
   cd Knome_desktops
   ```

2. **Ejecutar el instalador**:
   ```bash
   ./install.sh
   ```

---

## ⚙️ Requisitos

- **KDE Plasma 6** con **KWin Wayland**.
- **Python 3** con el paquete `python-evdev` (usado por el servicio de `Meta + Rueda`).
  - En **Arch / Manjaro / CachyOS**: `sudo pacman -S python-evdev`
  - En **Fedora**: `sudo dnf install python3-evdev`
  - En **Ubuntu / Debian**: `sudo apt install python3-evdev`
  - *Nota*: Tu usuario debe pertenecer al grupo `input` para leer eventos del ratón (`sudo usermod -aG input $USER`).

---

## 🛠️ ¿Qué hace `install.sh`?

1. Instala el efecto `gnomeoverview` en `~/.local/share/kwin/effects/gnomeoverview`.
2. Asigna la tecla `Meta` / `Super` para abrir y cerrar el GNOME Overview.
3. Activa la opción para mantener los escritorios virtuales exclusivamente en la pantalla principal.
4. Habilita el servicio de usuario de systemd `gnome-meta-scroll.service` para el cambio de escritorio con `Meta + Rueda`.
5. Recarga la configuración de KWin en caliente.

---

## 🧪 Tests

Para ejecutar la suite de pruebas unitarias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r <(echo "pytest")
pytest -v tests
```

---

## 📄 Licencia

GPLv2 o posterior.

