# Third-party notices

The production embedded UI uses only project source and the Go standard
library. The source checkout retains these reviewed dependencies and their
licenses:

- `github.com/creack/pty` v1.1.24 - MIT - `assets/LICENSE.creack-pty.txt`
- `github.com/gorilla/websocket` v1.5.3 - BSD-2-Clause - `assets/LICENSE.gorilla-websocket.txt`
- `@xterm/xterm` 6.0.0 - MIT - `assets/LICENSE.xterm.txt`
- `@xterm/addon-fit` 0.11.0 - MIT - `assets/LICENSE.addon-fit.txt`

The xterm files are retained under `terminal-assets/` for future optional
development, but are not embedded in the size-bounded firmware binary. The
firmware UI is `WEB_UI.html` plus `assets/app.js`; it renders all remote data
through `textContent`.
