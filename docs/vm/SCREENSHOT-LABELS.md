# Screenshot labels in this directory — one correction

The files `28a-…`, `29a-…` were originally written by a worker as "engineering-mode … rendered". They are **not** the engineering
window: they are the home screen's EV page (Battery / Range widgets, blue title bar), i.e. surface `2080`.

The engineering window itself, captured here after its six data queries were fully answered (`Pending Err` count **0**), is
`30-engineering-window-black-data-answered-2026-11-04.png`: a title bar reading **Engineering Mode** over a **black body**.

So the earlier conclusion in `docs/engineering-mode/engineering-data-services.md` — that answering those D-Bus queries fixed the black
page body — **does not hold**. The queries are genuinely answered now (verified by counting `Pending Err` lines in the DLT log: six or
more before, zero after), and the body is still black. The blank paint is therefore a QML/paint-layer problem, not a data problem, and
the next diagnostic is the application's own `qmlLog` output (it logs `AppMain.qml : Component.onCompleted` and `idAppRoot.width` /
`height`), not more adaptors.

`31-home-screen-STR_CAMERA_ALERT2-2026-11-04.png` is what surface `2080` actually renders, for comparison.
