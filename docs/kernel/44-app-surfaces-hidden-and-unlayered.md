# App surfaces are created, registered, then hidden and left unlayered — the shell UI is what is on screen

Date: 2026-11-08. **Offline analysis only. No QEMU run.** Source: the retained export payloads in
`evidence/controlled-run-3-2026-11-08/export-payload.bin` (157,860 B) and
`evidence/controlled-run-4-2026-11-08/export-payload.bin` (98,122 B).

This answers the protocol half of run 3's open question — "why does a registered surface not reach the
visible output" — from evidence already on disk.

## What the two protocols are, and why the distinction matters

Both payloads contain two similarly named interfaces. They are not the same thing:

| Interface | Direction | Meaning |
|---|---|---|
| `ivi_surface` | compositor → application | the application-facing surface object; `configure(w,h)` and `visibility(n)` are **server events** telling the app about its surface |
| `ivi_controller_surface` | controller client → compositor | the controller-facing wrapper; `visibility(n)`, `layer(…)`, `destination_rectangle(…)` are **requests** that set layout policy |

Reading a `visibility(0)` on `ivi_controller_surface` as "the app hid itself", or a `visibility(1)` on
`ivi_surface` as "the app asked to be shown", would be wrong in both directions. This is the same
name-collision trap recorded in `docs/kernel/40`.

## What happens to the AppHomeScreen surface

From run 3, in protocol order (timestamps are protocol ms):

```
[3028644.247] ivi_application@17.surface_create(1000, wl_surface@15, new id ivi_surface@20)
[3028644.726] ivi_hmi_requester@18.create_hmi_client(1, 1000, "AppHomeScreen", new id ivi_hmi_client@21)
[3028644.875] ivi_controller@11.surface_create(1000, new id ivi_controller_surface@22)
[3028644.922]  -> ivi_controller_surface@22.opacity(1.000000)
[3028644.948]  -> ivi_controller_surface@22.source_rectangle(0, 0, 0, 0)
[3028645.159]  -> ivi_controller_surface@22.destination_rectangle(0, 0, 1, 1)
[3028645.236]  -> ivi_controller_surface@22.orientation(0)
[3028645.261]  -> ivi_controller_surface@22.visibility(0)
[3028645.290]  -> ivi_controller_surface@22.layer(nil)
[3028645.324] wl_surface@15.set_buffer_transform(0)
[3028645.358] wl_surface@15.commit()
[3028645.414] ivi_controller_surface@22.set_destination_rectangle(0, 0, 1920, 720)
[3028645.473] ivi_hmi_client@21.set_display_plane(1)
```

Read in order, that is:

1. the app creates IVI surface **1000** and registers as an HMI client;
2. a controller client creates the controller-side wrapper and sets it **visibility(0)** and
   **layer(nil)** — hidden, with no layer to be composited into;
3. the app's `wl_surface@15.commit()` is **not preceded by any `attach()`**, so no buffer is ever
   supplied;
4. the destination rectangle is then set to the full 1920×720 and the display plane to 1, which would
   matter only if the surface were visible and layered.

So the surface exists, is registered, is sized — and is explicitly not displayed.

## The census that makes it decisive

Across run 3's entire payload:

| Request | Count |
|---|---:|
| `ivi_controller_surface@N.visibility(0)` | **10** |
| `ivi_controller_surface@N.visibility(1)` | **0** |
| `ivi_controller_surface@N.layer(nil)` | **10** |
| `ivi_controller_surface@N.layer(<number>)` | **0** |

**No surface in the captured window is ever made visible, and none is ever given a layer.** That is
not specific to AppHomeScreen; it holds for every client in that window.

## Which surface *is* on screen

Surface **30000** behaves completely differently, and its behaviour is on the `ivi_surface` (app-facing)
side:

```
wl_shm_pool.create_buffer(new id wl_buffer@9, 0, 1920, 720, 7680, 0)
wl_surface@3.attach(wl_buffer@9, 0, 0)
wl_surface@3.damage(0, 0, 1920, 720)
wl_surface@3.commit()
[13:39:43.178] Surface id(30000), Weston surface W(1920), H(720)
ivi_surface@7.configure(1920, 720)
ivi_surface@7.visibility(1)
```

It attaches a real 1920×720 `wl_shm` buffer, commits it, is configured at 1920×720, and receives
`visibility(1)`. Surface 30000 is the shell UI delivered by
`/usr/libexec/weston-ivi-shell-user-interface`, which is present in the image and is the only thing
drawing.

**That is the KIA splash captured in run 3** (`evidence/controlled-run-3-2026-11-08/display-*.png`,
byte-identical at +10/+60/+110 s). The screen was showing the shell UI the whole time, while every
app surface sat hidden and unlayered.

## Run 4 differs, and how

Run 4 shows `visibility(0)` ×8, `visibility(1)` ×2, `layer(nil)` ×6. The two `visibility(1)` values are
on `ivi_surface@7` — the shell surface again, not an app. So the difference between the runs is in how
far the window got, not in the app getting shown.

## Ownership caveat, preserved

The `ivi_controller` requests appear on a connection that binds `ivi_controller`; several such binds
occur in the payload (`@11` recurs because object ids are connection-local). **Which process owns that
connection is not established by this log**, and `docs/kernel/40` already recorded that object ids do
not identify processes. So the accurate statement is:

> A controller client set the new app surface hidden and unlayered at registration time.

Not: "the window manager hid it", and not: "the app hid itself".

## What this changes

The blocker is **not** that the app fails to draw, and it is not that the compositor is blind to it.
The surface is created, registered, sized and given a display plane. What never happens is that
anything makes it **visible and layered**.

That moves the candidate mechanism to layout policy: something must set `visibility` and a `layer` for
the app surface. The long-standing candidate — a "home ready" / HMI-controller signal that triggers
layout, recorded in `docs/vm/57` and `docs/kernel/38` — now has a concrete observable to check: does
`visibility(1)` and a numeric `layer(...)` ever get sent for an app surface, and what precedes it?

## The project-wide scan, performed

The first proposed action was carried out during the same session, offline, over **every retained
payload**: the two controlled-run payloads plus all 65 `work/vm/kbuild/ws/runs/*/exported-weston.bin`.

```
for p in evidence/controlled-run-*/export-payload.bin work/vm/kbuild/ws/runs/*/exported-weston.bin; do
  numeric layer : grep -c 'ivi_controller_surface@[0-9]*\.layer([0-9][0-9]*)'
  visibility(1) : grep -c 'ivi_controller_surface@[0-9]*\.visibility(1)'
done
```

**Result: no matches, in any capture.** Not one `ivi_controller_surface` in the project's retained
history is ever given a numeric layer, and not one is ever set `visibility(1)`.

That extends the run 3 census from one window to every window the project retains. It also means the
"what precedes `visibility(1)`" question **cannot be answered from existing evidence** — the event does
not occur anywhere in it.

## What that implies, stated carefully

- The app-side behaviour is not the blocker: surfaces are created, registered, sized and given a
  display plane.
- The layout-policy side never assigns a layer or visibility to an app surface, in any retained
  capture.
- Therefore, on this projection, **nothing in the retained evidence shows an app surface ever reaching
  the screen.** The KIA splash is the shell UI (surface 30000) drawing on its own.
- This is consistent with the long-standing "home ready" / HMI-controller hypothesis
  (`docs/vm/57`, `docs/kernel/38`), but it does **not** confirm it. Consistent-with is not evidence
  for a specific mechanism, and no trigger has been observed.

## Next exact action

Two candidates, and they should be distinguished before any boot:

1. **The trigger is absent from the projection.** If the signal that makes layout assign visibility and
   layers comes from a component the VM does not run, then no amount of capturing will show it. The
   check is static: find what in the vendor image calls `ivi_controller_surface_set_visibility` /
   `set_layer` with a non-zero argument, and whether that component is started in this projection.
2. **The trigger exists but our capture window never reaches it.** Then a run with the export trigger
   re-anchored to protocol progress (`docs/vm/63`) would show it.

Option 1 is cheap, offline, and decisive if it succeeds. It should be tried first — the same
"find the author of the request" move that resolved the `screen_create` question in `docs/kernel/40`.

---

## CORRECTION (same session): I attributed the hiding to a client, and the protocol says otherwise

The section above says "a controller client set the new app surface hidden and unlayered at
registration time". **That attribution is wrong**, and the retained protocol XML settles it.

`tools/uk_fw/ias_backend_soft/ivi-controller.xml`, interface `ivi_controller_surface`:

| Kind | Methods |
|---|---|
| **requests** (client → server) | `set_visibility`, `set_opacity`, `set_source_rectangle`, `set_destination_rectangle`, `set_configuration`, `set_orientation`, `screenshot`, `send_stats`, `destroy` |
| **events** (server → client) | `visibility`, `opacity`, `source_rectangle`, `destination_rectangle`, `configuration`, `orientation`, `pixelformat`, `layer`, `stats`, `destroyed`, `content` |

So in the payload:

- `ivi_controller_surface@22.visibility(0)`, `.layer(nil)`, `.source_rectangle(0, 0, 0, 0)` — **no
  `set_` prefix, therefore events**. They are the compositor **reporting the surface's layout state**,
  not a client asking for it.
- `ivi_controller_surface@22.set_destination_rectangle(0, 0, 1920, 720)` — **has `set_`, therefore a
  request** from a controller client.
- `ivi_controller@11.surface_create(1000, …)` — a request, so a controller client did create the
  wrapper.

The corrected reading of the sequence is therefore:

1. the app creates IVI surface 1000, registers as an HMI client, and commits **with no `attach()`**, so
   no buffer exists;
2. a controller client creates the controller-side wrapper (`surface_create`) and sets the destination
   rectangle to 1920×720 (`set_destination_rectangle`);
3. the compositor **reports** the resulting layout state as `visibility(0)`, `layer(nil)`,
   `source_rectangle(0, 0, 0, 0)`.

**What is observed, and it is the same conclusion as before:** the surface's layout state is hidden,
unlayered and has a zero source region — and across every retained capture, no `ivi_controller_surface`
ever reports `visibility(1)` or a numeric layer.

**What is no longer claimed:** that a client "hid" the surface. The state is a property of the
layout, and the requests that produced it are not fully identified. This is the third time in this
project that a direction or naming ambiguity nearly produced a confident wrong attribution — see
`docs/kernel/33` and `docs/kernel/40`. The rule that caught it was checking the XML for
`request` vs `event` rather than inferring from the method name.

Ownership of the `ivi_controller` connection is still not established, and `docs/kernel/40` already
recorded that object ids do not identify processes.
