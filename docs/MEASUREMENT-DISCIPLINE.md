# Measurement discipline: the mistakes this project actually made

Nine corrections were made in a single working session. Every one had the same shape: a plausible conclusion drawn from a measurement that could not have
supported it. They are collected here as rules, each with the concrete case, because the cases are more persuasive than the rules and because the next person will
make the same ones.

---

## 1. Check the instrument before you believe the result

**The case.** The root password hash of V-049 was tested against 10,000 plausible candidates and "no match" was nearly recorded. The tool was
`/usr/bin/python3`'s `crypt`, which on that host implements **DES only and silently ignored the `$6$` salt** — it was never computing SHA-512-crypt at all. Two
tells: `crypt.methods` listed only `METHOD_CRYPT`, and 2,000 "hashes" completed in 0.00 s, which is impossible for a 5,000-round algorithm. Redone with
`openssl passwd -6`, validated by checking the output shape for the known salt, the sweep was real (and still found nothing).

**Rule.** Before trusting a negative, prove the instrument can produce a positive. A tool that silently degrades to a different algorithm will answer confidently
and wrongly.

## 2. Search for the artefact, not the mechanism

Three separate false absences came from this:

| Claim | What was searched for | What actually shipped |
| --- | --- | --- |
| "the ASF parser is absent" | a file named `lms_asf.so` | `app/lib/lightmediascanner/plugins/asf.so` |
| "the MAC policy has no rules" | writes to `/sys/fs/smackfs/load2` in scripts | `/etc/smack/accesses.d/` — 27 files, 636 rules, loaded by `smack.service` |
| "nothing enables the encryption" | callers of `fde_test_v2.sh` | the flag is *read* from a module parameter, not recomputed |

**Rule.** If you are looking for data, look for the data. Absence of a write site does not mean absence of the artefact; a configuration file is not a script.

## 3. One variable at a time, and remember which ones you changed

**The case.** V-053 was reasoned down to "the encryption never engages" from the shipped flow. A later run showed `/dev/mapper/rw_data_enc is active` — encryption
had engaged. Both were true: the run had an **instrument** that forced `optUNECE=1`, and `esinit` reads that flag rather than recomputing it. My own hand changed the
behaviour under study.

**Rule.** Keep a list of every injected file, forced parameter and wrapper in a boot. When two of your own runs disagree, suspect your own instruments first.

## 4. "Black" is a conclusion, not an observation

**The case.** A display was called broken for several sessions. The surface existed at 1926×753 the whole time and was simply **not placed** on screen; one
`ivi-wm <id>` call made the interface visible. Later, the engineering window was called unpainted until `strace` showed the app had sent **624 bytes of Wayland
traffic, all object-id teardown, no `attach` and no `commit`** — it was waiting to be *shown* by the app manager.

**Rule.** Say what was measured: `pid=NO_VIEW` is not "input is broken", a capture size is not "rendering is broken". Distinguish *nothing drew* from *nothing was
visible* from *nothing was asked to draw* — they have three different causes.

## 5. A correlated line is not a cause

**The case.** `random: weston urandom read` appeared in two runs and was used twice as evidence about a boot branch. It appears in **both** the working and the
broken case, and no unit in the image even starts weston — some unidentified path invokes it. The line proved nothing either time.

**Rule.** Before a log line becomes evidence, find the code that emits it and confirm it can only be emitted on the branch you claim.

## 6. Negative controls turn a result into evidence

**The case.** The demonstration that `/etc/fde_test_v2.sh`'s passphrase opens its own container reported
`OPEN_WITH_1234_RC=0`. On its own that could mean the container was created with **no** passphrase. Adding `OPEN_WITH_RC_WRONG=5` — a wrong passphrase failing —
is what made it evidence.

**Rule.** Every "it worked" needs a matching "the wrong thing does not". Prefer a probe that also prints its own precondition: the invalid MAC probe failed because it
never printed the object label it had tried to set.

## 7. Verify the marker, not the exit code

**The case.** Two scripted documentation edits were skipped when a heredoc failed mid-way, and the `git commit` still succeeded — with only the files that happened
to exist. Caught by grepping for the expected new heading and finding `0`.

**Rule.** After any scripted edit, assert the change is present. A clean exit from the tool that was supposed to make the change proves nothing about the file.

## 8. Label the instrument in the artifact

Every projection-only addition in this repository says so in a comment and in the changelog: the MICOM SPI stand-in, the `/usr/bin/weston` wrapper, the pixman
solid-fill shim, the `lge_usb_adapter` neutralisation, the SMACK probe drop-in. Two of them changed the behaviour being studied.

**Rule.** If a finding depends on a modified system, the modification is part of the finding. Otherwise "it works in the projection" quietly becomes "it works on the
vehicle".

---

## The one-line version

**State what you measured, with the raw line; prove the instrument could have produced the other answer; and change one thing at a time — including the things you
changed yourself.**

## 9. Count the lines; do not read a number that is sitting where a count goes

**The case.** An audit log showed entries ending in `audit(615.831:21528)`, and `21528` was very nearly written up as "21,528 audit records" - which would have made audit volume look
like a plausible cause of CPU starvation and sent someone chasing it for an hour. It is the kernel audit subsystem's cumulative **serial number**. The actual record count was **600**,
one per second, which eliminates the hypothesis instead of supporting it.

**Rule.** When a quantity matters, compute it from the data (`grep -c`, a sum over the field you mean) rather than from a number that merely appears in a plausible position. Serial
numbers, timestamps, offsets and PIDs all live where counts live.

## 10. Verify the write, and verify that your verification ran

**The case.** A scripted edit to the register printed that it had recorded a finding. The insertion had actually matched nothing, so the file was unchanged - and the verification step I ran afterwards printed `0`, which I read as "the phrase may be phrased differently" and moved past. Two commits later the register was still asserting the opposite of what the evidence sheet said. The check existed, ran, produced the answer, and was ignored.

The earlier version of this rule, from §7, was "verify the marker, not the exit code". This one is one step further out: **the marker check has to be asserted, not printed.** A count of zero next to a phrase you expected is a failure signal, not a note.

**Rule.** After a scripted edit, assert positively - `grep -q` the exact new phrase and exit non-zero if it is absent - rather than eyeballing a number. And when a verification produces an unexpected value, stop the commit; do not reword the search and carry on.


## 11. A byte size is a hint about which frame you captured, never a verdict about what it shows

**The case.** This project has used PNG byte sizes as a shorthand for state for days: 129,844 is the
early background, 120,5xx is the application's standby face, ~16,000 is the laid-out home screen. It
worked often enough that "compare the size" became the first check.

It broke on 2026-11-05. A worker captured `docs/vm/39-…png` at **131,845 bytes** and treated it as
evidence that a CAN injection had been applied. I opened it: 1920x720, dark, title bar, **KIA logo, no
widgets** - the **standby face**, the powered-off presentation. So one standby frame is 120,5xx and
another is **131,845**, an 11 KB spread that is larger than the gap between two of the "reference"
sizes this project quotes. The run had never powered the application on, so the injection could not
have shown anything.

**Rule.** Size tells you whether you captured *something new*. Only the image tells you *what*. When a
state claim matters, describe the frame in words that a second person could check without your file -
"KIA logo and no widgets" versus "Battery and Range placed with placeholder dashes" - and open it.
Two frames of the *same* state can differ by more than two frames of *different* states.

**Corollary for delegation.** A worker told "compare against these reference sizes" will treat a
mismatched size as a state change. Give workers the **visual** test as well, in words, and require them
to say which surface id a capture came from.

## 12. A serial channel translates your bytes; only text survives it unchanged

**The case.** A capture was sent raw over a file-backed serial device to get it off the guest losslessly.
The PNG arrived mangled: magic `89504e47 0d0d0a 1a0d0a` instead of `89504e47 0d0a1a0a`. The line discipline
rewrites `\n` (0x0A) to `\r\n`, so **every 0x0A byte in a binary payload gains a 0x0D**.

**Rule.** Treat any serial channel as a **text** channel. Send binary as base64 with no newlines (base64
never contains 0x0A), or explicitly switch the port to raw mode first. Verify by checking the first bytes
of what arrives, not by comparing lengths - a length that grows by a few percent is the signature of this
exact fault.

**Corollary.** The same applies to the console: it is a log channel. Anything larger than a few KB, or
anything that is not text, belongs on a dedicated file-backed device.
