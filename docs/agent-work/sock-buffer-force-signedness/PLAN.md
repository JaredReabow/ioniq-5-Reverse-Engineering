# Plan — exact CVE-2016-9793 socket-buffer signedness audit

## Objective

Determine whether the recovered EU `260128` kernel retains the negative
`sk_sndbuf`/`sk_rcvbuf` machine-code premise fixed by upstream commit
`b98b0bc8c431e3ceb4b26b0dfc8db509518fb290`, without creating a socket,
issuing a socket option, using a capability, executing target code, or importing
an operational exploit.

## Method

1. Bind the exact `vmlinux`, Build ID, configuration, and authoritative
   embedded-kallsyms range for `sock_setsockopt`.
2. Retrieve and hash the authoritative upstream fix and public source context.
3. Confirm both force-option `CAP_NET_ADMIN` gates and their pass/fail branches.
4. Trace the send and receive doubling, signed minimum comparisons, conditional
   selections, and stores in the exact recovered instructions.
5. Distinguish ordinary buffer capping from force-option flow and determine
   whether either force route can store a negative doubled result.
6. Add a Boolean-only tri-state model with exhaustive tests and deterministic
   UTF-8/LF output.
7. Keep installed identity, runtime capability possession, syscall policy,
   invocation, corruption, crash, privilege gain, root, and persistence
   separate.
8. Run focused and complete validation before a path-limited commit.

## Non-goals and safety

No socket, `setsockopt`, option value, namespace, capability use, target
execution, malformed input, memory pressure, crash attempt, privilege action,
firmware modification, flash operation, or persistence action. Rejection of
this named CVE does not establish general networking or kernel safety.
