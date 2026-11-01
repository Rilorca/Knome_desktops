import json, pathlib, re

ROOT = pathlib.Path(__file__).parent.parent / "gnomeoverview"
UI = ROOT / "contents/ui"
qml = {p.name: p.read_text() for p in UI.glob("*.qml")}

def test_metadata_valid():
    m = json.loads((ROOT / "metadata.json").read_text())
    assert m["KPackageStructure"] == "KWin/Effect"
    assert m["X-Plasma-API"] == "declarativescript"
    assert m["KPlugin"]["Id"] == "gnomeoverview"

def test_all_effect_api_is_shimmed():
    used = set()
    for n in ("ScreenView.qml", "DesktopBar.qml", "DesktopView.qml"):
        used |= set(re.findall(r"\beffect\.(\w+)", qml[n]))
    main = qml["main.qml"]
    for name in used:
        assert re.search(r"(property \w+ %s\b|function %s\b)" % (name, name), main) or name in {"searchTextChanged", "configuration"}, name

def test_no_broken_desktop_switch():
    for n, s in qml.items():
        assert not re.search(r"SceneView\.currentDesktop\s*=", s), n

def test_milou_search_integration():
    screen_view = qml["ScreenView.qml"]
    assert "import org.kde.milou as Milou" in screen_view
    assert "Milou.ResultsView" in screen_view
    assert "id: searchResults" in screen_view
    assert "queryString:" in screen_view

def test_gnome_tweaks():
    assert "gridUnit * 8" in qml["DesktopBar.qml"]
    assert "verticalDesktopBar: false" in qml["ScreenView.qml"]
    assert "Easing.OutQuint" in qml["ScreenView.qml"]
    assert "opacity: 1  // panels" in qml["ScreenView.qml"]

def test_shortcut_handler():
    assert 'name: "GNOME Overview"' in qml["main.qml"]
    assert "sequence: effect.configuration.Shortcut" in qml["main.qml"]

def test_desktops_only_on_primary_config_and_qml():
    config_xml = (ROOT / "contents/config/main.xml").read_text()
    assert '<entry name="DesktopsOnlyOnPrimary" type="Bool">' in config_xml
    assert '<default>true</default>' in config_xml

    config_ui = (ROOT / "contents/ui/config.ui").read_text()
    assert 'name="kcfg_DesktopsOnlyOnPrimary"' in config_ui

    main_qml = qml["main.qml"]
    assert "property bool desktopsOnlyOnPrimary" in main_qml

    screen_view = qml["ScreenView.qml"]
    assert "isPrimaryScreen" in screen_view
    assert "visible: container.isPrimaryScreen" in screen_view
    # Secondary screen does not slide or shift desktops
    assert "deltaColumn: container.isPrimaryScreen ?" in screen_view
    assert "deltaRow: container.isPrimaryScreen ?" in screen_view
    assert "visible: container.isPrimaryScreen ? (gridVal > 0 || nearCurrent) : current" in screen_view
    assert "enabled: container.isPrimaryScreen && overviewVal > 0" in screen_view

def test_install_script_enables_virtualdesktopsonlyonprimary():
    install_sh = (ROOT.parent / "install.sh").read_text()
    assert "virtualdesktopsonlyonprimaryEnabled" in install_sh
    assert "DesktopsOnlyOnPrimary" in install_sh

def test_overview_mouse_wheel_navigation():
    screen_view = qml["ScreenView.qml"]
    # Function to step desktop smoothly with boundary checks and wrap-around support
    assert "function stepDesktop(" in screen_view
    assert "virtualDesktopNavigationWrapsAround" in screen_view

    # Both MouseArea (with acceptedButtons: Qt.NoButton) and WheelHandler
    assert "id: overviewWheelArea" in screen_view
    assert "onWheel: (wheel) =>" in screen_view
    assert "container.stepDesktop(" in screen_view

    # WheelHandler with touchpad and modifiers support
    assert "id: overviewWheelHandler" in screen_view
    assert "acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad" in screen_view
    assert "acceptedModifiers: Qt.NoModifier | Qt.MetaModifier" in screen_view

    # Correct per-desktop background binding
    assert "desktop: mainBackground.desktop" in screen_view
