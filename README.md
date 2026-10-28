# IONIQ 5 reverse-engineering research

Research notes, source tools and validation tests for a 2021 UK-origin
Hyundai IONIQ 5 Standard Gen5W infotainment system. The documented methods
and compatibility assessments distinguish official package evidence,
owner-supplied observations and community reports.

This public repository was initialized from a sanitized snapshot with fresh
Git history. Raw diagnostic exports, device dumps and private working
records are not included. See [PUBLIC-RELEASE.md](PUBLIC-RELEASE.md) for the
publication boundary and [tests/README.md](tests/README.md) for validation.

The research documents software and subsystem behavior. It does not include
a tested vehicle modification, update procedure or claim that a community
method works on the owner's installed build.

## VM research

The [current technical handover](HANDOVER.md) records a VM-adapted boot of the
European Gen5W Linux kernel, authentic Home rendering, isolated AppNavi map
pixels, and the unresolved Home-to-Navigation transition. Authored guest
helpers and experiment scripts are in [vm/repro](vm/repro), with bounded
evidence and inspected screenshots in [vm/evidence](vm/evidence). See
[vm/README.md](vm/README.md) for the source mapping and local artifact
requirements.
