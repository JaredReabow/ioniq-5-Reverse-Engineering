package main

import "embed"

// embeddedAssets contains the complete product UI. Requests are served through
// an explicit allowlist, so this filesystem is never exposed as a directory.
//
//go:embed WEB_UI.html assets/app.js
var embeddedAssets embed.FS
