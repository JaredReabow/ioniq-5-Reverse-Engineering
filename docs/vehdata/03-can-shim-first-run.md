# The CAN shim: the application's CAN setup is intercepted (first run)

Date: 2026-11-05. Tool: `tools/uk_fw/can_shim/can_shim.c`, built by `tools/uk_fw/can_shim/build.sh`.
Injected as `/can_shim.so` with `/etc/ld.so.preload` in the `work/vm/byhand` clone.

## What the shim does

Interposes `socket`, `bind`, `ioctl`, `setsockopt` and `close` **for `PF_CAN` sockets only** and hands
back one end of an `AF_UNIX`/`SOCK_DGRAM` socketpair. A detached thread writes a `struct can_frame`
datagram every 2 s into the other end, so the application's own `read()` returns a frame of exactly the
size it expects, with no `read` interposition at all. The frame is the SOC value a real vehicle logged:
**`0x2fc`, DLC 8, `00 00 12 00 00 00 00 77`** (byte 7 = 119 -> 59.5 %).

## What the run established

The shim was mapped into the application - `/proc/<AppHomeScreen>/maps` matched `can_shim` **4 times** -
and it fired:

```
567  CAN_SHIM_SETSOCKOPT
 81  CAN_SHIM_SOCKET            socket(PF_CAN, ...)
 81  CAN_SHIM_IFINDEX           ioctl(SIOCGIFINDEX)
 51  CAN_SHIM_BIND
 10  CAN_SHIM_IOCTL             other ioctls, accepted
```

**That is the empirical confirmation of the static mapping**: the home screen really does open
`PF_CAN` sockets and perform the interface-index/bind sequence. It is not a D-Bus path, which is what
`01-battery-range-data-path.md` argued from disassembly and what `02-partb-injection-attempt.md` failed
to contradict.

The **repeat count is the open question**: 81 sockets is not one listener. Either the application retries
when it does not like what it reads, or several components each open their own. That is the next thing
to read, and the shim already logs enough to tell them apart by adding the pid and the thread name.

## What this run did not establish

**Whether the widget shows a value.** The capture in this run was streamed as base64 over the console and
**corrupted** - 174,117 base64 characters for a 129 KB PNG, far past the ~8 KB that channel survives
(`docs/MEASUREMENT-DISCIPLINE.md`, and this project's runbook). That is my mistake, not the shim's.

**The fix, for the next run:** write the PNG to a real partition (`/log_data`) and read it from the host
out of that partition's file afterwards, instead of streaming it through the console. The serial console
is a log channel, not a file transfer channel.

## Status

- transport substitution: **installed and interposed** (measured)
- widget path is raw CAN: **confirmed by the application's own syscalls** (measured)
- widget value appears: **not yet measured** - the capture channel failed
