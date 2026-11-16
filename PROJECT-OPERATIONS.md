# VM continuation and record-keeping contract

Established 2026-10-26 from the owner's instructions.

## Objective and acceptance

Run the authentic Gen5W infotainment system fully in an isolated VM, reconstructing expected adapters, drivers, service contracts and persistence rather than substituting a dashboard or fabricating successful callbacks.

Current established milestones: adapted vendor-kernel boot; recovered userspace; authentic visible Home through the launcher/profile-confirm flow; isolated authentic navigation map pixels. Full Home↔Navigation is **not** accepted: latest manager sequence is `11/11 → 35/11 → 11/11`, with `notifyNaviLaunched[5] window[0]`.

Next bounded task: trace the producers of status `5` and window `0`, and the consumer transition from `APP_NAVI_LOADING` (35) to `APP_NAVI` (30). Reuse saved disassembly and runtime evidence before another expensive VM run. Do not replace the notification with a fabricated success. After integration, reconstruct evidence-derived data-bearing micom/CAN and persistence contracts. Broader full-system acceptance still needs an explicit feature matrix (audio, input, navigation, storage, suspend/restart, and hardware-dependent features).

## Immediate resumed checkpoint

The bounded fault observer captures real early-client stack/register evidence,
but the `-4` value does not establish original width `-1` or a runtime width
transition. A three-seat Council accepted the **measurement plan only** at
fingerprint `c59ac8a0d4ece96fd8fab5fe8a6795789697c95394d6e548a02dc8484052bbb5`.
Measure pre/post fields, update outcome, EGL call-site arguments and actual
resolved copy-entry arguments before any compatibility adaptation.

The plan/packet and validated Parallelism ledger are under
`navigation-contract-audit/orchestration/`. EC-01 and EC-02 require the direct
DeepSeek API provider using `deepseek/...`; OpenCode, OpenRouter, Codex Router
and other intermediaries are forbidden fallbacks. The live tool currently
rejects `deepseek/deepseek-v4.1-flash` as unknown. Do not substitute a provider,
implement the observer, or run the authentic VM without a supported direct route
or explicit selection of another direct DeepSeek model. Investigation I-001 remains qualified for
the mixed VM graphics stack, not stock-device exploitability.

## Durable records

- `HANDOVER.md`: read current top sections first; older embedded continuation sections contain superseded blockers.
- `Ioniq5-CHANGELOG.md`: editable, newest-first summary. Existing detailed milestones were retained, not recreated.
- `Ioniq5-HISTORY.md`: **append only**. Never rewrite existing entries, including obsolete conclusions. Append an explicit correction and source instead. Backfills must identify themselves as retrospective.
- `Ioniq5-VULNERABILITIES.md`: separate defensive vulnerability/remediation register; distinguish confirmed behavior from candidates and modification-created hazards.
- `evidence/corrections-log.md`: claim-level corrections. This overrides older claims, but itself contains historically bounded statements.

Preserve pre-existing dirty/untracked work. Do not auto-commit, push, flash, install packages globally, or change model/router configuration. Keep VM disks, temporaries and evidence project-local. No physical-device access, host-root operations or external VM networking is assumed.

## Worker routing policy (owner instruction, 2026-11-07)

Model selection is by task weight, not by convenience:

| Role | Route | Use |
|---|---|---|
| Grunt / dumb workers | **free OpenRouter models** — `codex-router/kilo-free/nvidia/nemotron-3-ultra-550b-a55b:free`, `codex-router/kilo-free/nvidia/nemotron-3.5-super-vl:free`, `codex-router/openrouter/openrouter/free` | Mechanical, verifiable, read-mostly work: log parsing, grep censuses, table building, diff inventories, doc-link audits. |
| Smart model / decisions | **Astra** (`codex-router/gpt-6-astra`), **Fable** (`anthropic/claude-fable-5-1`) | Root-cause ranking, protocol/ABI reasoning, run authorization, trade-off calls, review of worker output. |
| Blocked work | **shannon** family (`codex-router/shannon/...`), **daybreak blue** (`codex-router/gpt-daybreak-blue-latest`) | Only when an authorized task hits a security/approval block. Report the block; do not silently reroute. |

**Supervision is mandatory for free workers.** A free model's output is a *lead*, never evidence. Every free-worker claim must be re-derived by me or by Astra/Fable against the raw file before it enters the changelog, history, or vulnerability register. Free workers must never be given: write access to `Ioniq5-HISTORY.md` or `Ioniq5-VULNERABILITIES.md`, git commit/push authority, VM or QEMU execution, or any task whose failure mode is a fabricated measurement. Constrain each dispatch to one bounded, checkable question with a stated output format, and verify its answer mechanically afterwards.

Known failure modes to watch for in free-tier output: invented line numbers, summarised-instead-of-quoted log lines, confident claims from a truncated read, invented vendor behaviour, and silently substituting a nearby plausible value. Treat all four as expected until disproved.

## Orchestration and thread policy

Keep the **same chat/session** for scheduled continuation. Do not create new chat threads, child threads, or recursive agents. The latest repeated instruction specifies **up to 20 DeepSeek workers**, superseding the earlier 30-worker ceiling for now. The prior request assigned **Astra and Fable** planning, decisions, guidance and review; verified routes remain required. This is a ceiling, not a requirement to start 20 workers. Assign independent, nonduplicated questions, reuse retained evidence, and batch reviews. Shared-workspace writes must remain serialized unless separate workspaces and ownership are verified.

Current observed session metadata is `gpt-daybreak-blue-latest` via `codex-router`; it was not selected to evade a security restriction. Astra planning and Council routing were verified as `codex-router/gpt-6-astra` and `codex-router/gpt-6-sol`. The live worker tool rejects the required direct route `deepseek/deepseek-v4.1-flash` as unknown. Its suggested `opencode/...` route was probed historically but is now explicitly disallowed; it does not satisfy direct-provider policy. Runtime is unavailable until a `deepseek/...` model is exposed and authenticated. **Correction:** the exposed `spawn_worker` tool does support inline model-selectable delegation without a new chat thread; earlier statements that only child-thread delegation existed were mistaken. A useful read-only DeepSeek dispatch was attempted through that tool, but the host returned `store.runWorkerToolResult is not a function`. No worker result or execution metadata was obtained; completion and actual inference routing remain unverified. The current blocker is this host integration failure, not the no-new-threads constraint. Do not retry the same dispatch blindly or create a child thread as a workaround. No worker task completion is verified and no model identity is claimed from self-report. One inline DeepSeek dispatch attempt returned the host error described above; whether it initiated underlying inference is unknown. A fresh read-only Fable routing check failed: `openrouter/claude-fable-5.1` is in the catalog but is not advertised for native subagents (`multi_agent_version` must be `v2`). Enabling that exact route requires the operator's documented Router settings and a host restart; no configuration change or paid test was made. Do not silently fall back to a different route or separate API/CLI agent.

Security or approval restrictions must be reported and handled within authorized scope, not evaded by switching to another model. No Daybreak Blue execution route has been verified here.

## Scheduled continuation

**Owner requested retaining the existing task.** Latest listing found `206efda3-54ed-456c-a4f5-07b272247cc9` (`keep going`) **paused**; cadence was not exposed. Attempts to update its instruction/target were rejected by scheduler validation because interval schedules reject the time/timezone fields required by the exposed tool schema. No successful update, replacement task, or new thread is claimed. Stop retries until the tool schema is repaired or the task is edited in the UI. Do not assume the existing task is already bound to this chat. Set the task's `session_id` to the existing chat (`01a17741-b3c5-71c5-b44c-a4e9f3184bcd`), never omit it. Local scheduled tasks run only while pi-gui is open; they do not guarantee uninterrupted context or execution.

Proposed instruction:

> Continue the IONIQ 5 authentic infotainment VM project in THIS EXISTING CHAT ONLY. DO NOT create a new chat thread, child thread, or recursive agent. Read PROJECT-OPERATIONS.md, the current top of HANDOVER.md, and the latest changelog/history entries. If work is already running, do not start duplicate runs or edit its files. Otherwise continue one bounded, evidence-driven task toward authentic full-system VM operation, starting with the unresolved Navigation status/window contract. Preserve existing work, isolation and approval boundaries; do not fabricate vendor state/callbacks, flash devices, push commits, or switch models to evade security restrictions. Use DeepSeek workers only if a verified native route becomes available without creating chat threads, at most 20 and with explicit non-overlapping scope; otherwise report the delegation blocker. Update the editable changelog and handover at meaningful checkpoints, append only to history, and record security findings with evidence and remediation in Ioniq5-VULNERABILITIES.md. State what was actually verified and the next exact action. If blocked, record the blocker rather than retrying indefinitely.

## Validation

Use `/opt/homebrew/bin/python3.13` for local scripting; default `python3` is known broken. Full unit suite:

```sh
mkdir -p work/test-tmp
TMPDIR="$PWD/work/test-tmp" $PYTHON_WITH_CRYPTO \
  -m unittest discover -s tests -p 'test_*.py' -v
```

Tests are not Council acceptance or proof of complete VM functionality. Retain artifact identities and copy-on-write checkpoints before image mutation.
