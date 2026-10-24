import QtQuick
import org.kde.kwin as KWinComponents

// Fork of KWin's built-in Overview (src/plugins/overview). The C++ effect API that
// the upstream QML expects is emulated below with plain QML properties.
KWinComponents.SceneEffect {
    id: effect

    property bool activated: false
    readonly property int animationDuration: effect.configuration.Duration

    // ---- shim of OverviewEffect's C++ API used by ScreenView/DesktopBar ----
    property string searchText: ""
    property bool filterWindows: false
    property bool ignoreMinimized: false
    property real organizedGrid: 1
    property real gestureThreshold: 0.5
    property real overviewPartialActivationFactor: activated ? 1 : 0
    property real gridPartialActivationFactor: 0
    property real transitionPartialActivationFactor: 0
    property bool overviewGestureInProgress: false
    property bool gridGestureInProgress: false
    property bool transitionGestureInProgress: false
    function desktopOffsetForScreen(screen) { return Qt.point(0, 0); }
    function getView(edge) { return null; }
    function activateView(view) {}
    // ------------------------------------------------------------------------

    property var mainDelegate: Qt.createComponent("ScreenView.qml?" + Date.now())
    delegate: mainDelegate

    Instantiator {
        model: effect.configuration.BorderActivate
        KWinComponents.ScreenEdgeHandler {
            mode: KWinComponents.ScreenEdgeHandler.Pointer
            edge: modelData
            onActivated: effect.toggle()
        }
    }

    KWinComponents.ShortcutHandler {
        name: "GNOME Overview"
        text: "Toggle GNOME Overview"
        sequence: effect.configuration.Shortcut
        onActivated: effect.toggle()
    }

    Timer {
        id: hideTimer
        interval: effect.animationDuration
        onTriggered: { effect.visible = false; effect.searchText = ""; }
    }

    function toggle() { activated ? deactivate() : activate(); }
    function activate() {
        if (activated) return;
        hideTimer.stop();
        visible = true;
        activated = true;
    }
    function deactivate() {
        if (!activated) return;
        activated = false;
        hideTimer.start();
    }
}
