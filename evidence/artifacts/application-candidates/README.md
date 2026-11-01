# Application candidate artifacts

Reviewed, bounded excerpts supporting application-layer security findings.

- `applauncher-dbus-launch-evidence.txt` binds the exact recovered AppLauncher Request adaptor, runtime path propagation, process-object gates, signature-selection byte, direct QProcess start, verified-path failure handling, and shipped service/session-bus configuration for V-028.
- `smack-privileged-exec-chain-report.json` is the independently accepted, deterministic tool-version-`1.3.0` canonical-policy/source report for the direct configured `App::*` read/execute admission to the floor-labeled update anchor, script-interpreter preservation of `SMACK64EXEC=Privileged`, ELF credential commitment, and subsequent `onlycap` eligibility. It leaves installed xattrs, live credentials/capabilities, complete interpreter success, environment influence, effective SMACK override, root, and persistence unknown (SHA-256 `c4cfa148c93a437ce3eb87656c6d7458e4c7b3869c9270be33c28df5933b46cf`). Assessment: [`../../smack-privileged-exec-chain.md`](../../smack-privileged-exec-chain.md).

These excerpts are evidence for specific static claims, not runnable applications, D-Bus messages, launch requests, payloads, or proof of owner-unit reachability.
