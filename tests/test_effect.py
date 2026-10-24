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
        assert re.search(r"(property \w+ %s\b|function %s\b)" % (name, name), main) or name in {"searchTextChanged"}, name

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
