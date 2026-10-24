// Meta + wheel: previous/next virtual desktop (no wrap-around, as in GNOME).
function stepDesktop(delta) {
    print("gnomedesktopscroll: step " + delta);
    var list = workspace.desktops;
    var i = list.indexOf(workspace.currentDesktop);
    var n = i + delta;
    if (i < 0 || n < 0 || n >= list.length) return;
    workspace.currentDesktop = list[n];
}

// KWin's script engine may not expose Qt.* / KWin.* enums; fall back to the raw values.
var META = (typeof Qt !== "undefined" && Qt.MetaModifier) || 0x10000000;
var AXIS_UP = (typeof KWin !== "undefined" && KWin.PointerAxisUp !== undefined) ? KWin.PointerAxisUp : 0;
var AXIS_DOWN = (typeof KWin !== "undefined" && KWin.PointerAxisDown !== undefined) ? KWin.PointerAxisDown : 1;

registerAxisShortcut("GNOME Desktop Scroll: previous", "Previous virtual desktop (Meta+wheel up)",
                     META, AXIS_UP, function () { stepDesktop(-1); });
registerAxisShortcut("GNOME Desktop Scroll: next", "Next virtual desktop (Meta+wheel down)",
                     META, AXIS_DOWN, function () { stepDesktop(1); });
