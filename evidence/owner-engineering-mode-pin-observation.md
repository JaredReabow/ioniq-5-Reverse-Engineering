# Owner report: European Gen5W engineering PIN accepted

Recorded 2026-10-27 (Australia/Sydney). The owner reported that `19480717`
"worked" on the UK-origin 2021 IONIQ 5 head unit. This is direct user-reported
vehicle evidence, not an independently captured screen or diagnostic log.

The owner later supplied USB log exports. A 2026 runtime trace identifies the
installed software as `NE_E.EUR.S5W_L.001.001.250604`; see
`vehicle-usb/README.md`. The menu that opened has not
yet been identified. The code's acceptance does not establish what settings
that menu exposes, or show that an AppNavi replacement or firmware
modification is possible.

This supersedes the categorical compatibility table in
`gen5w-public-exploit-ecosystem.md` that labels `19480717` inapplicable to the
Linux unit. The local EU `260128` firmware's
`AppEngineerMode_PinCodeKeypad.qml` assembles eight digits for engineering mode
and passes them to native `AppEngineerModeEngine.checkPassWord()`. The QML then
branches on the **return value** `21` or `11`; those values are menu selectors,
not entered PINs. The local package is comparison evidence and is not proven to
be the build installed on the car.

Follow-up evidence to capture: the heading of the menu opened and whether it
is read-only. The firmware build is established by the supplied runtime log,
not by the accepted code alone. Do not infer an update path from the code.
