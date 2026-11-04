# VM runbook — how to run it, interact with it, and what to check

Practical instructions for the current state of the projection. Every command here has been run at least once
unless marked otherwise; every "check" is a thing to look at, not a thing to assume.

---

## 0. What you need

- The harness: `tools/uk_fw/vm_boot.py` with the workspace `work/vm/softbackend` (image clone + `prepare.json`).
- Host Python: **`python3.13`** (the default `python3` is broken for spawning on this host).
- QEMU installed (`qemu-system-x86_64` on PATH).

The scripts referenced live **inside the guest** (`/run-chain23.sh` etc.), injected with `debugfs`. To change them,
edit on the host, write into the image, and refresh the hashes in `prepare.json`:

```python
import json, hashlib
from pathlib import Path
w = Path('work/vm/softbackend'); p = w/'prepare.json'; d = json.load(open(p))
for n in d['sha256']:
    d['sha256'][n] = hashlib.sha256((w/n).read_bytes()).hexdigest()
json.dump(d, open(p,'w'), indent=1)
```

## 0b. Drive the VM live instead of scripting it (preferred)

    python3.13 tools/uk_fw/vm_console.py

That wraps `vm_boot.run(..., interactive=True)` and hands you the guest shell: you type, the guest runs it. Two things are worth
knowing about it.

- **It must go through `vm_boot`, not a hand-written QEMU command.** The boot needs the **SDHCI compatibility patch** applied over
  the QEMU debug socket. Without it the guest stops at `Waiting for root device /dev/mmcblk0...` and never reaches userspace. A
  hand-rolled `qemu-system-x86_64` line reproduces that stall exactly, which is what a first attempt here did.
- **Kill stray QEMU processes before measuring anything.** Six abandoned instances from earlier sessions were still running and
  starved TCG so badly that a boot which normally reaches userspace in ~40 s was still at `3.4 s` of kernel time after 200 s, and a
  prompt never appeared. `pgrep -fl qemu-system-x86_64` first, then `pkill -f qemu-system-x86_64`.

Inside the console, `/run-live.sh` reports what is up and prints the exact commands for the session.

## 1. Run the chain (vendor backend, single output, input module loaded)

```python
import sys; sys.path.insert(0,'tools/uk_fw')
import vm_boot as vb
from pathlib import Path
vb.run(Path('work/vm/softbackend'), True,
       "cd /tmp\nexport XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0\n"
       "sh /run-chain23.sh >/tmp/chain.out 2>&1 &\nsleep 50\necho DONE\n",
       timeout=200.0, memory_mib=2048)
```

**Check — use the right process name.** The compositor is `/usr/bin/weston-headless`, so its process name is
**`weston-headless`**, not `weston`:

```sh
pidof weston-headless      # the compositor — this is the one that matters
pidof weston               # EMPTY even when the compositor is healthy
pidof AppHomeScreen        # the home screen application
pidof keeper               # the long-lived ivi-shell user-interface placeholder
```

`pidof weston` returning nothing has already produced several false "compositor died" conclusions. Do not use it.

## 2. Launch engineering mode

```sh
export DBUS_SESSION_BUS_ADDRESS=$(cat /tmp/session_appmgr)
mkdir -p /tmp/app/bin
cp /app/bin/AppEngineerMode /tmp/app/bin/AppEngineerMode
dbus-send --session --dest=com.lge.avn.applauncher /Request \
  com.lge.avn.applauncher.request.launch int32:301 string:AppEngineerMode \
  string:/tmp/app/bin/AppEngineerMode
```

**Check — it needs 45–70 seconds to appear.** Poll, do not sleep a fixed short interval:

```sh
for i in $(seq 1 8); do sleep 8; P=$(pidof AppEngineerMode); \
  [ -n "$P" ] && { echo "up: $P"; readlink /proc/$P/exe; break; }; done
```

Expect `readlink` to print `/tmp/app/bin/AppEngineerMode`. Its DLT log should show
`AppEngineerModeEngine::getEnterPasswordCnt()` — i.e. the PIN logic is running.

**Check the frame:**

```sh
timeout 25 /usr/libexec/weston-screenshooter    # writes ./wayland-screenshot.png
```

Current expectation: a **4,117-byte black frame**. On the vendor backend the failure is *black*; the *striped*
frames were specific to the ten-output research backend.

## 3. Interact with it (touch injection)

The vendor module `/weston-vm-input.so` accepts commands over `/tmp/weston-vm-input`:

```sh
echo 'click 960 360'      > /tmp/weston-vm-input
echo 'drag 960 360 960 500' > /tmp/weston-vm-input
```

**Check — the compositor acknowledges each command in its log:**

```
VM_INPUT_CLICK_ACCEPTED
VM_INPUT_FOCUS_BEFORE_MOVE pid=NO_VIEW
VM_INPUT_FOCUS_AFTER_MOVE  pid=NO_VIEW
VM_INPUT_CLICK_DONE
```

- `CLICK_ACCEPTED` + `CLICK_DONE` = the injection path works.
- **`pid=NO_VIEW` = nothing is under those coordinates.** The click is delivered and no surface receives it. That is the
  black screen seen from the pointer's side, and it is the current blocker: the input stack is fine, the view is absent.
- If the module is not loaded you get **no `VM_INPUT_` lines at all** — check the compositor config contains
  `modules=/weston-vm-input.so`.

## 4. What is verified, and what is not

| Claim | State |
| --- | --- |
| Compositor runs on the vendor backend | **verified** (`pidof weston-headless`) |
| Chain survives; home screen launches | **verified** (pid present, launcher log shows `m_AppProcess->start`) |
| Engineering mode launches from the dev path via app id 301 | **verified** (`readlink` + `getEnterPasswordCnt`) |
| Touch injection reaches the compositor seat | **verified** (`VM_INPUT_CLICK_*`) |
| A view exists under the pointer | **no** — `pid=NO_VIEW`, frame is black |
| PIN typed in and `IpConfigShell` reached | **not attempted** |
| HID keyboard in the projection | **blocked** — udev does not run under the research init and the module stack failed to load by hand. A harness gap, not a vehicle property |

## 5. Common false readings (all of these have happened here)

- `pidof weston` empty → **not** a dead compositor; the name is `weston-headless`.
- `wait $PID` inside a subshell returns **127** ("not a child of this shell") — never the child's status.
- `ias-shot` writing a `.png` that is really ASCII **PPM**; check the magic, not the extension.
- A capture succeeding does **not** prove the compositor is alive.
- The chain's own teardown kills the compositor after ~155 s of dwell — a checkpoint after that measures the teardown.
- Measuring before the application appears: engineering mode needs 45–70 s, the home screen ~40 s.

---

# What to do on a physical unit, and what to check

**Everything below is untested by this project.** It is what the evidence says to try, ordered by risk.

## A. Engineering mode entry (the only no-privilege route)

1. Car on (ACC or engine), unit booted.
2. **Settings → General → About** (some variants: a blank area at the bottom of About).
3. **Tap the software version number 5–10 times, quickly.** A keypad should appear.
4. Enter **`19491003`** (engineer) or **`2400`** (dealer).

**Check and record**: does the keypad appear; which PIN is accepted; the exact menu list you then see — specifically
whether **Encryption Update** and **Force Update** are present or hidden. Photograph each screen. Note the software
version shown on the About screen so the result is attributed to a specific build.

**If the keypad appears but the menu is short** (only *Scheduled Update List*), that is the production/SOP state this
project measured in code — expected, not a failure.

## B. If and only if engineering mode opens

- Look for **IpConfigShell**. The external project describes it as shell-command execution. If it exists, it is the
  strongest facility on the unit — **treat the unit as rooted from that point**.
- Before touching **Force Update** or **Encryption Update**, read `docs/DOWNGRADE-POSSIBILITIES.md`. Force Update passes
  the version compare; Encryption Update is documented as ignored on production builds.

## C. Downgrade — what to check, in this order

1. **Does the About/version screen show a build date?** Record it; everything below depends on it.
2. **Is there any "previous version" list** under engineering update? If it only *displays* versions, it is not an
   installer.
3. **Anti-rollback is the open question.** If you can obtain the vendor's own older firmware *for that exact model and
   region* (signed, unmodified), an ordinary USB update attempt is the cleanest experiment: if it installs, anti-rollback
   is absent or weak on that build; if it refuses with a version error, it is strict. Record the error text verbatim.
4. **Do not** attempt modified or unsigned packages — the RSA check rejects them, and a half-written slot is how units
   are bricked.

## D. What not to do

- Do not interrupt an update once started.
- Do not attempt anchor replacement (V-034) on a vehicle you need.
- Do not assume the About gesture exists on your model because it exists on another — this project has only inferred it
  for the IONIQ 5.
