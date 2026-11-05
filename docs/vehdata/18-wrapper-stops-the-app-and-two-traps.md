# Wrapping the application binary stops it starting at all

Date: 2026-11-05. Attempt: put a `/bin/sh` wrapper at `/app/bin/AppHomeScreen` that exports `WAYLAND_DEBUG=1`
and execs the renamed real binary, so the protocol trace would land in the application's own log.

## What happened

```
X1_PIDS=[]           nothing matching AppHomeScreen.real
LOGSZ=               the application's log file did not exist at all
X1_CTX=0
```

**The application never started.** Not "started and failed to paint" - **no process, no log, nothing.** A
`/bin/sh` script in place of the binary is refused (or never executed) somewhere between the launcher and the
process.

I did not establish which of these it is: an **integrity check** on the binary, an `exec` that requires an ELF,
or a launcher-side path table that treats the entry as data. **Stating it as unproven is the honest position**,
and the reason it matters is that an integrity check here would be a finding in its own right.

## Two traps this attempt exposed

1. **`debugfs` in this build has no `rename` command.** I assumed it did, wrote the wrapper over
   `/app/bin/AppHomeScreen`, and **destroyed the vendor binary inside the clone**. It was recovered from the
   pristine extraction (`work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/AppHomeScreen`,
   15,636,960 bytes, verified `\x7fELF`), and the clone is back to the shipped layout: one binary, no `.real`,
   no drop-in.
   **Rule:** write the copy to the *new* name first and verify it, then replace the original. Never overwrite a
   vendor file in the same step as an unverified assumption about the tool.
2. **A wrapper is an instrument, and this project's instruments keep breaking the application under test** -
   the preload broke its Wayland connection, the placement tool raced its surface, and now a wrapper stops it
   launching. That is three for three.

## Where the debug trace has to come from instead

**The compositor, not the application.** Weston can be told to log protocol traffic, and the failing event is
delivered *by the compositor* - so the server side is the natural place to ask. That also keeps the change
inside this project's own component (the compositor is the vendor's, but the module list and environment around
it are ours), rather than modifying a vendor application binary.

**Next:** enable the compositor's protocol debug output and read which request the compositor answered for an
object the client had already destroyed. If the compositor's log cannot be made to say that, the alternative is
a **small protocol proxy** between the application and the compositor - more work, but it sees both directions
and cannot alter the vendor binaries.
