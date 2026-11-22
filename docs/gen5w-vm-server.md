# Gen5W VM Workbench in your browser

The launcher starts a local browser UI for the Gen5W simulator and keeps a terminal open with setup steps, command output, elapsed time, progress, and the chosen address. The browser shows VM startup status, then displays guest frames and sends gated input. The guest uses a snapshot with its network adapter disabled. Wi-Fi controls, when enabled, drive a simulation.

This 0.4.2 package is a **developer preview for people who already hold the exact compatible prepared Workbench assets**. It is not a stock-update converter and it does not download those assets. Without them, setup stops at asset admission and the interactive VM cannot start. The snapshot-backed rootfs uses an explicit backend name for compatibility with QEMU 8.2. The guest still sees the same SD device and has no network adapter.

The retained 0.3.5 macOS candidate completed one changed zero-input qualification
with the exact private assets: acquisition finished inside the unchanged
deadline, a historical frame was followed by fresh 1920x720 compositor frames,
and clean shutdown removed the owned VM and service resources. This qualifies
that macOS run only. Version 0.3.6 reports physical asset-copy progress, refuses
an insufficient destination before buffered copying, and continues startup when
optional Windows browser handoff fails. Its changed Mac run verified the full
asset set, then retained a native Confirm timeout before any frame or input.
Version 0.3.7 records bounded optional timings around the existing post-receipt
checks; malformed timing metadata cannot replace the acquisition result. It does
not change the two log scans, identity/hash/inode gates, error precedence, or the
15/20-second deadlines. Version 0.3.8 applies the existing
`max,vendor=GenuineIntel,-avx2` profile only to QEMU TCG on Linux/WSL2 ARM64 and
reports the selection in the runtime event/status surface. macOS and x86-64 keep
`max,vendor=GenuineIntel`. The full-assets 0.3.8 Linux ARM64 run showed none of
the earlier crash signatures and stopped later at the foreground D-Bus
`reason11` timeout. Version 0.3.9 classifies why the already bounded DLT failure
snapshot was unavailable using fixed states only; it adds no bus monitor and changes no
foreground call, timeout, scan or acquisition outcome. Version 0.4.0 separates
a nonzero status from the existing final-byte check pipeline (`read_failed`)
from a successful zero newline count (`newline_check_failed`) without retrying
the check or changing the acquisition result. The generated command enables
`pipefail`, and its fixtures cover an upstream-only `tail` failure. Version
0.4.1 removes the standalone screenshot's whole-second timeout guard from the
IVI-only tail because that tail does not consume the calculated timeout. The
strict 15-second capture/receipt and 20-second verification boundaries remain.
Version 0.4.2 keeps an incomplete reason-11 trace unavailable while deriving a
fixed, failure-only summary from bounded complete records before the partial
tail. It reports only whether handler entry or draw progress was observed in
that admitted prefix; absence is explicitly not proven, and no raw DLT content
is published. It changes no success, frame, capture, input, identity, or timeout
gate.
Successful Linux
rendering, physical installation and restoration remain separate evidence
boundaries.

**Stop VM** also cancels startup or closes the service after an asset-admission failure. Its response acknowledges the stop request even when no VM backend became ready; the original startup failure stays available for diagnosis.

## First launch

1. Download and extract the GitHub source archive, or clone the repository.
2. Supply the compatible local VM inputs described below.
3. Open the launcher for your platform.

| Host | Launcher | Dependency setup |
| --- | --- | --- |
| macOS | Double-click **Gen5W.command** in the **launchers** folder. You can also run it from Terminal. | Native QEMU and other missing packages through [Homebrew](https://brew.sh/). |
| Linux | Open **Gen5W.desktop** from the checkout or run the **start.sh** script in a terminal. Some desktops require you to allow the downloaded desktop file to launch. | Native QEMU with APT, DNF, or Pacman. Other distributions can supply compatible tools already on PATH. |
| Windows | Double-click **Gen5W.cmd** in the **launchers** folder. | Ubuntu on [WSL2](https://learn.microsoft.com/windows/wsl/install). The installer may ask you to restart Windows. Open Ubuntu once to create your Linux account, then reopen the launcher. |

The POSIX launchers require Python 3.10 or newer. They offer to install it using an available package manager. When a missing dependency requires a system install, the launcher shows the commands and asks before running them. Homebrew itself is an initial prerequisite on macOS when the system packages are missing. Windows uses PowerShell's process-scoped RemoteSigned policy. If Windows marks a downloaded script as remote and blocks it, inspect the script, then unblock that file in Properties and reopen the launcher.

Use **--plan** on macOS or Linux, or **-Plan** on Windows, to preview setup. The launcher keeps standard-library Python in a local **.venv**. If Zig is missing, it installs the SHA-256-pinned [Zig 0.13.0 release](https://ziglang.org/download/index.json) for your host into the local cache. It leaves any existing package-manager setup in place.

For a preauthorized remote run, use **Gen5W.cmd -Yes -NoBrowser** on Windows or **sh launchers/start.sh --terminal --yes --no-browser** in a terminal. This accepts the displayed dependency setup and suppresses launcher pauses. Linux package commands use **sudo -n** and the package manager's automatic confirmation flag, so first authorize sudo in your interactive Linux terminal if needed. Missing sudo authorization returns an error. **-NoPause** / **--no-pause** suppresses only the final pause and does not grant consent. The local asset manifest must still be present before dependency installation; exact hash verification occurs before VM preparation.

Windows UAC, a required reboot, and Ubuntu's initial Linux account creation remain desktop steps. **-Yes** cannot grant administrator privileges or answer those operating-system prompts. WSL installation returns **3010** after the prerequisite step to indicate that setup must resume; it does not report a running Gen5W service. If WSL/Ubuntu is absent, **-Plan** shows the complete deferred sequence and identifies downstream checks that could not yet run.

The Windows launcher reports optional nested KVM exposure from inside WSL2 after that distribution is available. A Windows **.wslconfig** setting of **[wsl2] nestedVirtualization=true** requests nested virtualization; it does not prove that **/dev/kvm** exists, that the Linux user can access it, or that KVM can create a VM. Review and preserve existing settings before editing; a distribution restart may be required. The retained x86 Gen5W VM always selects **QEMU TCG software emulation**. Enabling nested virtualization does not change that command, and ARM64 KVM cannot accelerate this x86 guest.

## VM inputs

The source archive contains the server and host-side tools. The EU 260128 profile expects a compatible prepared VM image and companion files that you supply locally. An original vehicle update archive alone cannot start the VM. Keep these local files out of Git.

The exact standalone source allowlist is recorded in **docs/gen5w-vm-server-files.txt**. It excludes firmware, prepared images, compiled helpers, captures and private evidence. The Wi-Fi simulator source retains its `AGPL-3.0-only` SPDX notice and the archive includes the local [GNU AGPL v3 text](../LICENSES/AGPL-3.0-only.txt). The public launcher does not turn a stock update into the required prepared image.

The standalone source archive also carries its focused test modules. From the extracted directory, run:

    PYTHONPATH=tools/uk_fw python3 -B -m unittest \
      tests.test_vm_boot \
      tests.test_vm_workbench_platform_config \
      tests.test_vm_workbench_runtime \
      tests.test_vm_workbench_assets \
      tests.test_vm_workbench_bootstrap \
      tests.test_vm_workbench_service \
      tests.test_vm_workbench_server \
      tests.test_vm_workbench_server_distribution \
      tests.test_vm_workbench_web_ui

These tests use synthetic fixtures and a real local HTTP service process. They do not install dependencies, start QEMU, prove a real Windows/Linux first run, or replace exact local asset admission. When PowerShell is available, the suite also executes the Windows launcher decision harness. Run that harness directly on Windows with:

    powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File tests\test_gen5w_windows_launcher.ps1

It checks real launcher functions and argument construction with bounded WSL fixtures; it makes no administrator changes or downloads. Its pass marker is **GEN5W_WINDOWS_LAUNCHER_TESTS_PASS**.

Place these files under **.gen5w/assets** in your checkout:

- **bzImage** and **rootfs.img** from the compatible prepared VM workspace.
- **manifest.bin**, **seed_dev.bin**, and **seed_user.bin**, the corresponding synthetic fixtures from the workspace.
- **startup.sh**, the hash-bound compatibility recipe retained with the prepared inputs.
- **libdbus-1.so.3**, the exact compatible guest library used to build the simulator helper.
- **gen5w-assets.json**, the manifest with the supported hashes. Generate it from the checkout after setting up Python:

      sh launchers/start.sh --print-asset-manifest > .gen5w/assets/gen5w-assets.json

The supported preparation route is to export these exact files from your own existing compatible Workbench 0.2.41 prepared workspace and locally obtained matching guest library. The built-in manifest then checks every byte against the supported profile. There is currently no public recipe that derives this profile from a stock update, and changing a pin to admit a different image is not supported.

On Windows, run that command in Ubuntu from the checkout path. Start the server through **Gen5W.cmd** so it also checks the Windows browser environment. macOS and Linux users can point at an alternate directory with **--assets PATH**. Use **--print-asset-manifest --wifi-sim** to see the additional files expected for the optional Wi-Fi simulator, and pass **--wifi-sim** or **-WifiSim** to enable it when those assets are present. The server verifies the supported profile and its file hashes before preparing a new workspace.

The Windows launcher translates and validates the Windows `explorer.exe` path inside WSL2, then passes that exact executable to the server as an argument-list browser handoff. Empty or failed **wslpath** output warns and continues with **--no-browser**, leaving the exact server address visible for manual opening. Use **-NoBrowser** to select that behavior explicitly. A successful browser-process launch is only a handoff; verify the page in the Windows browser before claiming browser qualification.

The prepared root filesystem must already contain the compatible guest-side runtime expected by the retained launch recipe. The optional Wi-Fi simulator also requires a host toolchain that reproduces its pinned target hash. Dependency discovery and fixture tests do not prove that every compiler build on Windows or Linux will reproduce that optional binary; a mismatch stops before VM admission.

## Local address

The default port is 8765. With a verified local hostname entry, open [http://gen5w.local:8765/](http://gen5w.local:8765/). The launcher otherwise opens [http://127.0.0.1:8765/](http://127.0.0.1:8765/) or prints the actual fallback address when the port changes.

To set up the hostname, run **sh launchers/start.sh --setup-hostname** on a macOS or Linux terminal, or **Gen5W.cmd -SetupHostname** on Windows. The launcher checks for conflicts and asks before any administrator action. The Windows launcher opens the Windows hosts file for an explicit edit. When offered the edit, add a separate line:

    127.0.0.1 gen5w.local # Gen5W Workbench

Remove that single line from the same hosts file to undo the change. Existing conflicting mappings need to be resolved outside the launcher. The server binds only to IPv4 loopback, and the launcher uses the alias only when it resolves to that address. Windows uses [WSL localhost forwarding](https://learn.microsoft.com/windows/wsl/networking) to reach the server.

An additional **::1 gen5w.local** entry is accepted as loopback. An IPv6-only alias still uses numeric IPv4 fallback because the server listens on IPv4. **-SetupHostname -Yes** leaves a missing Windows alias unchanged and prints the fallback; make the optional editor change once through an interactive launch.

For [http://gen5w.local/](http://gen5w.local/), request **--port 80** on macOS or Linux, or **-Port 80** on Windows. This requires the hostname plus a free port that the regular user can bind. When either is unavailable the launcher reports the fallback. The server and QEMU run with your regular user permissions.

## Stop, recover, and check what ran

- Use **Stop VM** in the browser to shut down the guest. Use **Ctrl+C** in the terminal to stop the foreground service.
- The shutdown JSON receipt is flushed before the foreground HTTP process closes. If an owned process misses both graceful and kill deadlines, Stop reports a failure, the launcher returns a failing status, and the runtime retains the process identity.
- The launcher shows the setup log path. The log records setup commands and results. Package-manager and server output is visible in the terminal. Each VM run records its own diagnostics in the state directory.
- The default state directory is **.gen5w** in the checkout on macOS and Linux. The Windows launcher uses a checkout-specific directory under **~/.gen5w** inside Ubuntu for Unix sockets, VM state, and the local Python environment.
- Startup can stop on an incompatible asset, a missing tool, or a VM admission failure. Read the terminal and browser error before starting a new run. On Windows, verify that the distribution is WSL2 and that **localhostForwarding** is available if the browser cannot reach the server.
- To reclaim storage, stop the launcher, keep any inputs and logs you want, then remove the local workspace. Keep package manager changes under the corresponding package manager.

Cross-platform command and launcher tests exercise setup paths with simulated tools. Full first-run qualification on each operating system depends on available test hosts and compatible local inputs.

Starting with 0.3.2, the browser can show a predefined startup stage for a
future HMI failure, for example `Gen5W HMI startup failed (standby_exited).`
This requires exact launcher status 25 and a verified private receipt for the
current run. Missing, invalid or conflicting receipts leave the message generic.
Startup failure keeps frames and controls unavailable, and raw guest logs stay
in the local state directory. Host fixtures cover this reporting. Real guest
receipt execution and interactive startup remain unverified in this release.
The earlier Linux status-1 failure stage and HMI crash cause remain unknown.
