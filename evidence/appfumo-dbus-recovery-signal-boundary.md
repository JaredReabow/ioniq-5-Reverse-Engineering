# AppFUMO wildcard D-Bus recovery-signal boundary

Status: exact-static, canonical-policy, execution-free analysis of the recovered
embedded FUMO ELF, streamed canonical rootfs, and exact kernel configuration.
No recovered target code or rootfs executable was run. No bus was contacted and
no signal, method, request, payload, packet, flash/update action, or persistence
operation was created.

## Conditional finding

The reviewed recovery subscription uses Qt 5's system-bus connection API with
empty service and path filters, fixed interface/member filters, and a bound
receiver/slot. Under Qt 5 semantics, empty service and path filters accept a
matching interface/member signal from any remote application on the same bus
and from any object path. The interface/member pair filters message identity; it
does not authenticate the sender.

Generated Qt dispatch can invoke the local recovery consumer. That consumer
checks a nonempty byte array, a normalized recovery-event value, and several
local state guards before tailing into a separate asynchronous recovery request.
The event value, outgoing request coordinates, and request argument value are
redacted. Static construction and asynchronous submission do not confirm that
MICOM accepts or performs an action.

Classification: **conditional wildcard-signal trust boundary**. If another
application can reach and participate in the same system bus and can emit a
matching signal, the subscription can deliver it to a configured-privileged
local consumer and may cause a separate asynchronous recovery request. This is
not message forgery, a demonstrated cross-label socket path, confirmed recovery
action, code execution, a root transition, or persistence.

## Exact subscription and local flow

The subscription setup FDE is `[0xe2790,0xe2c2b)`. At the connection call at
`0xe29df`, exact SysV argument setup establishes:

- the service QString is the Qt shared-null/empty QString;
- the path QString is independently the Qt shared-null/empty QString;
- the interface and member QStrings come from fixed literals;
- the receiver is the owning local object; and
- the old-style Qt slot signature is fixed and bound.

The retained package binds the three fixed values only by normalized role,
length, and SHA-256:

| Role | Length | SHA-256 |
|---|---:|---|
| recovery filter interface | 21 | `4d1d2f5d27522a35e3812ae4690003ef45c5a7981bb58a77afc5346b1537be41` |
| recovery filter member | 23 | `15f77bc4e3fc16792c9c0915a80b0276606cdc0995ec431614d42096ac91b762` |
| bound receiver slot | 29 | `7bac66793c29e5d146b03baeda34118afe6113537c169cd5b2b650257eb32e21` |

The generated dispatch FDE `[0x16df80,0x16efe4)` has one complete direct call to
the local consumer entry. The consumer FDE is `[0x11f060,0x11f1a9)`. Hash-bound
machine anchors cover the input existence/length/value tests, three local state
gates, one local helper result, and the tail at `0x11f11c` to the separate
request FDE `[0xe8d10,0xe907c)`.

The request code constructs one byte-array argument, appends one redacted value,
and submits asynchronously. Retained evidence does not publish the callable
outgoing service, path, interface, member, or argument value. No reply or
external state change is established.

## Canonical system-bus policy

The analyzer streams all `66,836` rootfs members and binds inventory SHA-256
`c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`.
The system policy directory contains exactly 18 direct regular XML members. Its
name-hashed inventory SHA-256 is
`5a952075294ad24ce6e601eef93e6dbabea5d15ff3c81d9dcd7dc851ff3c8df5`.
All 18 members are parsed, not searched as text.

The main `system.conf` contains 14 policy rules in total: 10 allows and four
denies. Its default-policy block is counted separately as 13 rules: nine allows
and four denies. That default block:

- has one rule allowing all users to connect;
- has one rule denying method-call sends;
- has one rule allowing signal sends; and
- has one rule allowing signal receives.

Those main-file counts are not folded into the policy-directory audit. The 18
`system.d` policy members separately contain 221 rules: 208 allows and 13
denies. Rule attributes are conjunctive. Within a defined policy order, the
last matching rule wins. Scope precedence is default, matching groups, matching
user, console-true, console-false, then mandatory; matching group policies have
undefined relative order. The main file's `includedir` is later than its default
rules, but the order of files within that directory is undefined. A material
same-scope allow/deny split across included files therefore has an **unknown**
outcome rather than being rejected as a contradiction. The exact normalized
recovery-signal audit found no material cross-file same-scope conflict.

None of the directory rules is an explicit allow or deny for the hash-bound
recovery interface/member, and none is an unconstrained general-signal rule.
The named `receive_sender` signal inventory is split into 15 allows and one
deny. One redacted sender (length 21, SHA-256
`508d97e50a6fa1dd3369295f5e1d748cd188a9ab297d3cec406c6eff9fc3b5a5`)
is shared by a default-scope signal deny and a root-user signal allow in one
policy member. For that sender, the later included default deny overrides the
main default receive allow for a non-root recipient; the root-specific allow
then overrides the default result for root. The installed consumer uid is not
established, so which outcome applies at runtime remains unknown. A named-sender
policy constraint also does not itself authenticate the origin accepted by the
Qt subscription.

All 137 `send_destination` values in `system.d` are named and non-wildcard;
none matches a destination-less broadcast. Their redacted normalized inventory
SHA-256 is
`51ecc6b7a2005b330a4ca29a2db2d19b676048ca29f6e9a6a28c9d56f168a79e`.
By contrast, `send_destination="*"` would match a destination-less broadcast,
and `receive_sender="*"` is a general receive constraint. Interface/member and
sender/destination attributes remain conjunctive when combined.

The selected MICOM policy has one root policy with an own grant and a
named-destination send grant for the same redacted service. Because that named
destination does not match the destination-less normalized signal, the policy
has no matching signal-origin, receiver, interface/member, or
sender-authentication grant. Root ownership and named-destination send
permission therefore do not authenticate broadcast signal origins.

There is no canonical `system-local.conf` member in this archive. The main file
nonetheless has an optional local include and a conditional SELinux-context
include. Archive absence is not proof that an installed runtime lacks a
replacement, generated include, overlay, or changed daemon configuration; those
effects remain unknown.

XML processing is fail closed over a documented supported subset. Each policy
file must have the approved external D-Bus configuration DOCTYPE, but the
analyzer performs no external resolution. It accepts exact `default` and
`mandatory` contexts, boolean `at_console` scopes, and nonempty user/group
scopes; group-scoped message policies are supported. It rejects malformed XML,
internal entity declarations, CDATA, duplicate or aliased archive names, links
and special policy members, nested or unexpected policy members, unexpected
includes, unsupported scope values/rule forms/attributes, empty identities,
unknown supported-subset message types, and mixed ownership or connection
attributes. Valid daemon rule forms outside this bounded subset are rejected
rather than silently approximated.

## Launcher, configured privilege, and labels

Canonical members bind the launcher unit, launcher script, AppLauncher binary,
outer AppUpgrade binary, and both label scripts by exact type, mode, size, and
content hash.

The launcher unit has no `User=` or `Group=` directive. A system service
therefore uses systemd's configured default root identity. Its start directive
selects the canonical launcher script; the script in turn selects AppLauncher.
The exact AppLauncher binary binds the dynamic process helper, AppProcess
construction span, process-start span, and AppUpgrade role literal by range
hash. This establishes the static process-construction route used for the
updater role, not the runtime dynamic pathname or a successful process start.

Both canonical label scripts name AppUpgrade's executable-label assignment. The
label value is retained only by hash/length in the strict manifest. Complete
installed runtime uid, process label, file label, launcher-selected pathname,
and successful exec remain conditional and unobserved.

## SMACK and daemon integration boundary

The exact kernel configuration SHA-256 is
`987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`.
Its canonical 3,430-entry inventory sets SMACK enabled and SELinux/AppArmor
disabled.

The canonical `dbus-daemon` is 485,784 bytes with SHA-256
`b1ce9266a8fa9c22c176472c03ab322f6a7e733dcf839f8044e00cc4d5e3519b`.
Its complete 3,930-string ASCII inventory has SHA-256
`62556c6ccae5efc58e2ef3c0cd66dbb7913fdfd79e0b13f423b47ef026a8768c`.
Thirteen strings name SELinux; none names Smack. This rejects only a tested
**named** Smack integration in this daemon artifact. It does not reject kernel
socket mediation, filesystem-label checks on the bus socket, unnamed integration,
or another runtime access-control layer.

Consequently:

- bus-policy permission is not same-bus socket reachability;
- configured uid root is not a SMACK escape;
- same-bus admission for an arbitrary label is unknown; and
- runtime uid/label evidence is still required before claiming a cross-domain
  path.

## Model distinctions and unknowns

The package preserves these non-equivalences:

- bus policy permission != same-bus socket reachability;
- wildcard filter != message forgery;
- interface/member match != authenticated sender;
- local slot invocation != MICOM action;
- uid root != SMACK escape;
- recovery control != code execution or root; and
- local asynchronous submission != accepted remote action.

Unknowns are the installed consumer uid/label, prospective sender uid/label,
arbitrary-label system-bus socket reachability, kernel socket mediation effect,
dynamic policy/include replacement, whether any matching signal is emitted,
whether the local slot runs, and whether MICOM changes recovery state.

## Exact identities and deterministic package

- embedded ELF: 5,066,264 bytes, SHA-256
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`,
  Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- canonical rootfs: 879,109,759 bytes, SHA-256
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- exact LLVM authority: Homebrew LLVM 23.1.3;
- complete decoded instruction inventory: 470,739 entries, SHA-256
  `693dce0d89faabeea30512fe0a696a733e9bdd64fd7be7379dba98a44d2dc0c8`;
- complete FDE inventory: 3,789 ranges, SHA-256
  `2c71813a3f098f8f949c6acee1080c0147df182e589f8b8b576798ce4807eb07`;
- analyzer: `tools/uk_fw/appfumo_dbus_recovery_signal_boundary.py`;
- byte-free selected evidence SHA-256:
  `4b0c525ee7ec862dfc65df2e4e0a991d5bb934708dfb8ba1f102110759a95ab7`;
- strict manifest SHA-256:
  `ff934574db6c0204c05f1e2a3766b83b5ea60394b366d2c9ec8c902db7b6e82c`;
- normalized report SHA-256:
  `826ed7c3fcfcd7077840fbad792a88737a2555ba9e2a528f1baf9179bd07a936`.

Final validation ran with `<platformio-env>/bin/python3`: the corrected focused
suite passed 15 tests and 19 subtests, and the bounded full `tests/` suite passed
797 tests and 351,505 subtests. The public harness passed with three pass, four
informational, and zero failed or blocked checks. Dual deterministic generation,
retained-report comparison, compilation, UTF-8/LF, privacy, and diff checks also
passed.

The analyzer emits fixed UTF-8/LF JSON through `sys.stdout.buffer`. It emits no
supplied paths, target instructions or bytes, callable D-Bus coordinates,
signal or argument values, commands, requests, payloads, packets, or exploit
steps.
