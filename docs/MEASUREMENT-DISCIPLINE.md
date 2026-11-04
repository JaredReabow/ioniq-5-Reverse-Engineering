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
