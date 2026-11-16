# Interacting with the VM: the recipe, and how to tell it worked

Everything here is measured on the authentic path (vendor kernel → `/lib/systemd/esinit` → the vehicle's
own `/usr/bin/weston` → the vehicle's own `AppHomeScreen`). Nothing here is inferred.

## 1. Boot it

```sh
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_partimg/run-byhand.py \
    --init /init-authentic-hmi.sh --smp 4 --timeout 700
```

`--smp 4` is **not** optional. At 2 vCPUs the managed application never registers its bus name, and
nothing below will work. Expect Multi-User at roughly **97 s** on the authentic path.

## 2. Wait for the right things

Three separate states, in this order, and the third is the one people miss:

| what to check | how | what it means |
|---|---|---|
| compositor alive | `pidof weston.real` (inside the guest) | `pidof weston` never matches; the binary is `weston.real` |
| app registered | `pidof AppHomeScreen` | the process exists |
| **app powered on** | the call in step 3 | **the home screen lays out** |

## 3. Power the vehicle on - this is what makes the layout appear

```sh
dbus-send --session --print-reply --dest=com.lge.hyundai.avn.appmanager /Information \
    com.lge.avn.appmanager.info.set_power_on_status int32:1 int32:0
```

Without it the application shows its **standby face** - title bar, a logo, a black menu bar - and there
is nothing to click. With it, the home screen lays out: Battery and Range widgets placed, light menu bar.
Reference frame: `docs/vm/38-gesture-home-layout-after-set-power-on-2026-11-05.png` (16,062 bytes).

Note what this call does **not** do: it does not change what `ask_power_status` returns (it reads `1`
before and after). It pushes a state event. Do not use the getter to check whether it worked - look at
the frame.

## 4. Click something

The input channel is a file the injected input module polls:

```sh
echo 'click 960 360'            > /tmp/weston-vm-input
echo 'drag 960 360 960 500'     > /tmp/weston-vm-input
```

Success is visible in **`/tmp/weston-real.log`**, and the sequence to look for is:

```
VM_INPUT_READY
VM_INPUT_CLICK_ACCEPTED
VM_INPUT_FOCUS_BEFORE_MOVE pid=<n> uid=0
VM_INPUT_CLICK_DONE
```

## 5. Look at the result - by surface, not by "newest"

```sh
cd /tmp && timeout 25 /usr/libexec/weston-screenshooter     # writes ./wayland-screenshot.png
```

**`weston-screenshooter` writes into the current directory**, so `cd /tmp` first. It composites *the
newest surface*, and **the background's surface is created last**, so a "successful" capture is often
the splash. Enumerate the surfaces in `/tmp/weston-real.log`, capture **each non-layer surface**, and
compare. Known reference sizes: **129,844** early background · **120,5xx** standby app · **~16,000**
laid-out home screen.

## 6. What is and is not established about clicking

- **Established:** clicks are accepted and routed; the module logs a focus target with its pid and uid.
- **Measured negative:** on the standby frame the focus target was **`weston.real` itself** (pid 797),
  *not* the application - so the earlier reading "the click reached a real client" was true and
  misleading at once.
- **Not measured:** whether a click now lands **on an application widget** after the layout appears.
  That is the next interaction measurement, and it needs a widget whose response is visible - which is
  why the Battery/Range work matters beyond the numbers.

## 7. Traps that cost this project real runs

| trap | reality |
|---|---|
| `pidof weston` | never matches - the binary is `weston.real` |
| `wait` in a subshell | returns 127 |
| a capture succeeded | proves only that the compositor answered, not that the app drew |
| guest writes to disk | never persist - `snapshot=on`; use the `-chardev file` channel for output |
| scripts in `/tmp` | `/tmp` is tmpfs; put guest scripts under `/run-*.sh` |
| a stray QEMU instance | starves TCG and makes every timing reading wrong - `pgrep -fl qemu-system-x86_64` first |
