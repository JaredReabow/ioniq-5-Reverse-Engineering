# The special-key payload, decoded: `[0x01, 0x05]` is the engineering-mode request

Date: 2026-11-05. Target: `ApplicationManager`, the slot behind
`com.lge.car.micom.can.NotifyKeyFrontSpecialEvent` (V-060).

## The decode, instruction by instruction

```
206308: movq   0x10(%rax), %rdx         QByteArray payload: data pointer at offset 0x10
20630c: movsbl 0x1(%rax,%rdx), %ebp     ebp  = payload[1]
206311: movsbl (%rax,%rdx), %r13d       r13d = payload[0]

2061d8: cmpl   $0x1, %r13d ; je 0x2062a0       payload[0] must be 1
2062a0: cmpl   $0x1, %ebp  ; je 0x206360       payload[1] == 1  -> branch A
2062a9: cmpl   $0xa, %ebp  ; je 0x2063d8       payload[1] == 10 -> branch B
2062b2: cmpl   $0x5, %ebp  ; jne 0x2061e2      payload[1] == 5  -> the engineering path
2062bb: movl   $0x12d, %esi                    301 = AppEngineerMode's app id
2062c3: callq  0x18e7b0                         ask(301) -> al
2062c8: testb  %al, %al ; jne 0x2061e2         if it answered TRUE, return - do nothing further
2062d0: callq  0x23f760
2062d5: movl   $0x47, %esi                      71
2062dd: callq  0x22da80                          ask(71) must equal 1
2062e2: cmpl   $0x1, %eax ; jne 0x2061e2
2062f0: movl   $0x5, %esi
2062f8: callq  0x1f6160                         the action that engages engineering mode
```

**So the payload is two bytes: `payload[0] == 0x01`, and `payload[1] == 0x05` is the engineering-mode
request.** `0x12d` = **301**, which is the app id this project has been chasing as "the only engineering
route" - it is reached from here, by a two-byte CAN-side key event, not by a screen gesture.

The guards are informative too: the path **bails out if `ask(301)` returns true**, then requires
`ask(71) == 1`, and only then acts. That is a state-qualified request, not a blind launch.

## What this does to the earlier negative

The nine-payload sweep (`array:byte:0x01,0x00` through `0x08`) **included `0x05`**. So the payload was
**already correct**, and the reason nothing happened is **not** the payload format - it is **delivery**.

That reframes the remaining obstacle cleanly, and it is a different kind of problem:

| hypothesis | status |
|---|---|
| payload format wrong | **refuted** - `[01 05]` decoded above, and it was in the sweep |
| no sender filtering | **measured** - empty service and empty path (V-060) |
| delivery blocked | **open and leading** - SMACK conjoins the bus, and V-056 records real `action=denied` entries for other services |
| a further state gate | **open** - `ask(71) == 1` is a precondition the projection may fail |

## The next test, precisely

Emit `[0x01, 0x05]` and watch **delivery**, not the outcome: run a `dbus-monitor --system` alongside the
emission, and grep the audit/SMACK log for a denial naming our sender. If the monitor shows the signal
and the app still does not start, the obstacle is the `ask(71) == 1` precondition. If the monitor shows
nothing, the obstacle is the bus or label policy - and that is a finding about the projection, not about
the vendor.

**Not established:** that engineering mode can be opened by this route in the projection. **Established:**
what the payload is, that it was correct when tested, and that the obstacle lies after the payload.

## Delivery measured: the signal reaches the bus and the manager does not act

Test run on the authentic projection, with a monitor watching the exact interface before the emission:

```
DL_HOME=2487 2449                     the home screen is running
dbus-monitor --system "type='signal',interface='com.lge.car.micom.can'" > /tmp/mon.txt &
dbus-send --system --type=signal /Can com.lge.car.micom.can.NotifyKeyFrontSpecialEvent array:byte:0x01,0x05
   -> Error org.freedesktop.DBus.Error.NoReply     (expected: --print-reply on a signal never replies)
DL_MON_LINES=6
DL_MON_SEEN=[1]                       the monitor SAW NotifyKeyFrontSpecialEvent on the system bus
DL_ENG_PID=        waited=60s          no AppEngineerMode
```

**The signal is emitted and observed on the bus. Delivery is not blocked** - not by the bus policy and not
by SMACK, at least not for the signal itself. And the manager still did not start the application in the
following 60 seconds.

So the obstacle is **logical, after the payload**, and the decode already names the candidates:

1. `ask(301)` at `0x2062c3` returning **true** makes the handler return immediately (`testb %al,%al; jne`).
   A "true" here plausibly means *the app is already considered requested/available*, and the handler
   treats that as done.
2. `ask(71) == 1` at `0x2062dd`/`0x2062e2` - a state flag the projection may not satisfy.
3. The signal matched the interface but not the manager's expectations of **sender ownership**: the
   connect passes an empty service, but Qt's `connect` with an empty service still records the *well-known
   name of the sender* in the message; a slot that inspects `message().service()` would see our client's
   unique name.

**Established:** payload correct, no sender filter, signal delivered, manager silent. **Not established:**
which of the three gates above is responsible - and that is now a question about one of two function
calls rather than about transport.
