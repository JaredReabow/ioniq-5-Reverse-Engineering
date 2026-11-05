# Plans, from three independent reviewers

Date: 2026-11-06. The two goals had reached a point where the next move mattered more than the next measurement, so three
planners were asked the same question independently, with the same repository state and the same constraints.

| plan | model | framing |
|---|---|---|
| `fable.md` | Claude Fable 5.1 | experiments and stopping rules |
| `astra.md` | GPT-6 Astra | critical path, CAN routes, what to cut |
| `daybreak-blue.md` | Daybreak Blue | remediation ranking and verification |

All three read the same files: `docs/CURRENT-STATE.md`, `docs/vm/45-backend-is-forced-not-chosen.md`, the two most recent
`docs/kernel/` measurements, `docs/root-access-paths.md`, `docs/REMEDIATION-REPORT.md` and
`docs/defences/controls-inventory.md`. None was allowed to run an experiment or patch a vendor binary; each was told to name
the offset and the trade if it proposed one.

**How to read them:** none is authoritative. They are three readings of one state by models that did not pay for the
measurements, and this project's own record has been wrong often enough tonight that outside readings are useful precisely
because they do not share its momentum. Where all three agree, that is the strongest signal available without running
anything. Where they disagree, the disagreement is the useful part.

**The standard each was held to**, from `docs/MEASUREMENT-DISCIPLINE.md`: every claim traceable to a file, a textual check
before a visual one, and a stopping rule written down before the next guess.
