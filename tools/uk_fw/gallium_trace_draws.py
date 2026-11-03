#!/usr/bin/env python3
"""gallium_trace_draws — read a Mesa Gallium trace dump and report its draws, the textures they
sample, and the texture coordinates on the quad vertices.

Why this parses XML and not an apitrace .trace
----------------------------------------------
It was assumed going in that the Gallium trace module writes an apitrace-compatible binary capture.
It does not. The in-use driver was inspected instead of trusted
(`work/software-egl/extracted/mesa18/usr/lib/x86_64-linux-gnu/dri/swrast_dri.so`, Mesa 18.2.8;
the Mesa 13.0.6 tree under `work/software-egl/extracted/mesa` is the same) and its .rodata contains
the trace module's complete output vocabulary:

    <trace version='0.1'>  <?xml version='1.0' encoding='UTF-8'?>
    <?xml-stylesheet type='text/xsl' href='trace.xsl'?>
    <call no='  ' class='  ' method='
    <int>%lli</int>  <uint>%llu</uint>  <float>%g</float>  <bool>%c</bool>
    <ptr>0x%08lx</ptr>  <null/>  <string>  <enum>  <array>  <elem>
    <struct name='%s'>  <member name='%s'>  <bytes>  </bytes>  </trace>
    and the literal hex alphabet 0123456789ABCDEF

So the dump is flat XML with a small, closed tag set, and byte blobs are written as uppercase hex by
table lookup (which is why no "%02x" format string exists anywhere in the binary). No apitrace
tooling, no `trace.xsl` needed, and no binary parser: this file is a text parser over exactly those
tags.

Two facts about this build that the analysis has to live with
------------------------------------------------------------
1. There is no return-value tag in the vocabulary above. The dump records arguments, not return
   values, so `create_sampler_view` does not say which pointer it produced. Where a create/use pair
   has to be joined (sampler views, sampler states, vertex-element states) this script pairs them
   positionally — each newly created object is matched to the next not-yet-seen pointer of that kind
   — and says so in the report, with a count of how many joins were ambiguous. That is an
   assumption about call ordering, not a reading of the trace. Vertex buffers need no such trick:
   `pipe_vertex_buffer.buffer` and the first argument of `buffer_subdata` are pointers recorded
   directly.
2. There is no `GALLIUM_TRACE_TRIGGER` in this build (no such string exists; the only GALLIUM_*
   literals are DDEBUG, DDEBUG_SKIP, DRIVER, DUMP_VS, HUD*, NOOP, NOSSE, PRINT_OPTIONS,
   PROCESS_NAME, RBUG, RBUG_START_BLOCKED, TESTS, THREAD, TRACE). Dumping therefore starts at screen
   creation and stops when the process dies, and is very likely to be killed mid-write. So the
   parser streams and treats an unterminated final <call> as normal, not as corruption.

What the report is for
----------------------
The measured artefact is a 3-pixel lateral offset per row, constant over 20 sampled row pairs. That
is a property of how the quad's texture coordinates advance down the image, so the question this
report answers is arithmetic: do the vertex texture coordinates contain a du/dy equal to three
texels per scanline? See the "shear test" section it prints, and the CONFIRM/REFUTE wording in
`GALLIUM_TRACE.md`.

Usage
-----
    gallium_trace_draws.py TRACE [options]

      --max-draws N     detail for the first N draws (default 8)
      --stop-after N    stop parsing once N draws have been detailed (default: whole file)
      --draw N          raw-dump call number N of the trace (schema check on a first run)
      --dump-call N     print the verbatim trace fragment for call N
      --gl-log PATH     cross-reference /tmp/gl-upload.log (glTexImage2D W/H lines)
      --expect-texels X shear magnitude to test against (default 3.0)
      --raw             also print attribute bytes as hex
      --buffer-cap MB   cap on retained vertex-buffer bytes (default 64)
      -q                summary only, no per-draw detail
"""

from __future__ import annotations

import argparse
import collections
import os
import re
import sys

# --------------------------------------------------------------------------------------------
# Wire format
# --------------------------------------------------------------------------------------------

# The trace is a flat sequence of <call ...> ... </call> elements inside <trace>. Reading it by
# splitting on the call boundary rather than with an XML parser is deliberate: (a) a trace killed
# mid-run is not well-formed XML and ElementTree would refuse it, losing everything; (b) traces of
# an animating UI are large, and this keeps memory to one call. An unterminated tail is dropped.
_HEAD = "<call "
_TAIL = "</call>"

_TAG = re.compile(
    r"<(?P<close>/?)(?P<tag>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?P<attrs>(?:\s+[A-Za-z_][A-Za-z0-9_]*='[^']*')*)\s*(?P<empty>/?)>"
    r"|(?P<text>[^<]+)"
)
_ATTR = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)='([^']*)'")


def iter_call_fragments(fh, chunk=1 << 20):
    """Yield the text of each complete <call>...</call> fragment, streaming.

    Returns (fragment, truncated_flag) for the final, incomplete call only if asked; here the
    incomplete tail is simply dropped, and the count of dropped bytes is reported by the caller
    via the file-size difference.
    """
    buf, started = "", False
    while True:
        block = fh.read(chunk)
        if block:
            buf += block
        while True:
            if not started:
                i = buf.find(_HEAD)
                if i < 0:
                    # keep a short tail: a tag could straddle the chunk boundary
                    if len(buf) > 32:
                        buf = buf[-32:]
                    break
                buf = buf[i:]
                started = True
            j = buf.find(_TAIL)
            if j < 0:
                break
            yield buf[: j + len(_TAIL)]
            buf = buf[j + len(_TAIL) :]
            started = False
        if not block:
            return


class Node:
    """One element of the dump. Leaves carry `.text`; containers carry `.kids`."""

    __slots__ = ("tag", "attrs", "kids", "text")

    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.kids = []
        self.text = ""

    def __repr__(self):
        return f"<{self.tag} {self.attrs} kids={len(self.kids)} text={self.text!r}>"


def parse_fragment(frag):
    """Parse one call fragment into a tolerant tree. Never raises: an unknown or malformed tag is
    skipped by one character so a single bad byte cannot abort a long trace."""
    root = Node("call")
    stack = [root]
    pos = 0
    n = len(frag)
    while pos < n:
        m = _TAG.match(frag, pos)
        if not m:
            pos += 1
            continue
        pos = m.end()
        text = m.group("text")
        if text is not None:
            t = text.strip()
            if t:
                stack[-1].text += t
            continue
        tag = m.group("tag")
        if m.group("close"):
            if len(stack) > 1:            # tolerate an over-closed tail
                stack.pop()
            continue
        node = Node(tag, dict(_ATTR.findall(m.group("attrs") or "")))
        stack[-1].kids.append(node)
        if not m.group("empty"):
            stack.append(node)
    # The fragment begins with its own <call ...> element; hoist its attributes so callers can ask
    # the tree itself for class/method instead of reaching into a child.
    if root.kids and root.kids[0].tag == "call":
        top = root.kids[0]
        root.attrs = top.attrs
        root.kids = top.kids
    return root


# --------------------------------------------------------------------------------------------
# Small enum tables. Only closed sets whose numbering is long-standing are named; anything whose
# numeric value could be wrong is printed raw rather than guessed.
# --------------------------------------------------------------------------------------------

PRIM = {
    0: "POINTS", 1: "LINES", 2: "LINE_LOOP", 3: "LINE_STRIP", 4: "TRIANGLES",
    5: "TRIANGLE_STRIP", 6: "TRIANGLE_FAN", 7: "QUADS", 8: "QUAD_STRIP", 9: "POLYGON",
    10: "LINES_ADJ", 11: "LINE_STRIP_ADJ", 12: "TRIANGLES_ADJ", 13: "TRIANGLE_STRIP_ADJ",
    14: "PATCHES",
}

TARGET = {
    0: "BUFFER", 1: "1D", 2: "2D", 3: "3D", 4: "CUBE", 5: "RECT", 6: "1D_ARRAY",
    7: "2D_ARRAY", 8: "CUBE_ARRAY",
}

WRAP = {
    0: "REPEAT", 1: "MIRROR_REPEAT", 2: "CLAMP_TO_EDGE", 3: "CLAMP_TO_BORDER", 4: "CLAMP",
    5: "MIRROR_CLAMP", 6: "MIRROR_CLAMP_TO_EDGE", 7: "MIRROR_CLAMP_TO_BORDER",
}

FILTER = {0: "NEAREST", 1: "LINEAR"}
MIPFILTER = {0: "NONE", 1: "NEAREST", 2: "LINEAR"}


def enum_name(table, raw):
    """Enum values may arrive as a number or, if the build dumps names, as text. Accept both."""
    if raw is None:
        return "?"
    if raw in table:
        return table[raw]
    try:
        return table.get(int(raw, 0), f"#{raw}")
    except (TypeError, ValueError):
        return str(raw)


# --------------------------------------------------------------------------------------------
# Argument access. Field nesting differs slightly between Mesa versions, so lookups are by member
# name anywhere inside the call rather than by fixed path.
# --------------------------------------------------------------------------------------------


def walk(node):
    yield node
    for k in node.kids:
        yield from walk(k)


class Args:
    def __init__(self, root):
        self.root = root
        self._members = collections.defaultdict(list)
        self._structs = collections.defaultdict(list)
        self._ptrs = []
        self._ints = []
        self._bytes = []
        self._collect(root, None)

    def _collect(self, node, member):
        if node.tag == "member":
            member = node.attrs.get("name")
        elif node.tag == "struct":
            self._structs[node.attrs.get("name", "?")].append(node)
        elif node.tag == "ptr":
            self._ptrs.append(node.text)
        elif node.tag in ("int", "uint", "float", "bool", "enum", "string"):
            self._ints.append(node.text)
            if member:
                self._members[member].append((node.tag, node.text))
        elif node.tag == "bytes":
            self._bytes.append(node.text)
        for k in node.kids:
            self._collect(k, member)

    # -- scalars -------------------------------------------------------------------------
    def first(self, name, default=None):
        v = self._members.get(name)
        if not v:
            return default
        return v[0][1]

    def num(self, name, default=None):
        v = self.first(name)
        if v is None:
            return default
        try:
            if v.lower() in ("t", "true"):
                return 1
            if v.lower() in ("f", "false"):
                return 0
            return int(v, 0)
        except ValueError:
            try:
                return float(v)
            except ValueError:
                return default

    def member_nodes(self, name):
        out = []

        def rec(n, m):
            if n.tag == "member":
                m = n.attrs.get("name")
            elif m == name and n.tag == "struct":
                out.append(n)
            for k in n.kids:
                rec(k, m)

        rec(self.root, None)
        return out

    def struct_members(self, node):
        d = {}
        for k in node.kids:
            if k.tag == "member":
                name = k.attrs.get("name")
                d[name] = k
        return d

    def structs(self, name):
        return self._structs.get(name, [])

    def ptrs(self):
        return self._ptrs

    def byte_blobs(self):
        return self._bytes


def parse_hex_blob(text):
    """<bytes> holds uppercase hex with the separators the C code chose, if any."""
    s = re.sub(r"[^0-9A-Fa-f]", "", text or "")
    if len(s) % 2:
        s = s[:-1]
    try:
        return bytes.fromhex(s)
    except ValueError:
        return b""


# --------------------------------------------------------------------------------------------
# Replay
# --------------------------------------------------------------------------------------------


class TexObj:
    __slots__ = ("idx", "res", "target", "fmt", "w", "h", "first_level", "last_level",
                 "swizzle", "ptr", "call")

    def __init__(self, idx, call):
        self.idx = idx
        self.call = call
        self.ptr = None
        self.res = None
        self.target = "?"
        self.fmt = "?"
        self.w = self.h = None
        self.first_level = self.last_level = None
        self.swizzle = None

    def dims(self):
        if self.w is None and self.h is None:
            return "?"
        return f"{self.w}x{self.h}"


class Sampler:
    __slots__ = ("idx", "wrap_s", "wrap_t", "norm", "minf", "magf", "mipf", "lod_bias",
                 "max_aniso", "call", "ptr")

    def __init__(self, idx, call):
        self.idx = idx
        self.call = call
        self.ptr = None
        self.wrap_s = self.wrap_t = None
        self.norm = self.minf = self.magf = self.mipf = None
        self.lod_bias = self.max_aniso = None


class Draw:
    __slots__ = ("call_no", "mode", "count", "indexed", "start", "views", "samplers",
                 "elems", "vbufs", "fb_w", "fb_h", "vertices", "note")

    def __init__(self):
        self.views = []
        self.samplers = []
        self.elems = []
        self.vbufs = []
        self.vertices = None
        self.note = ""


class Replay:
    def __init__(self, buf_cap):
        self.buf_cap = buf_cap
        self.buf_bytes = 0
        self.texobjs = []
        self.samplers = []
        self.buffers = {}                     # ptr -> bytearray (shadow of uploaded data)
        self.views_by_ptr = {}                # heuristic join: view ptr -> TexObj
        self.samplers_by_ptr = {}             # heuristic join: sampler ptr -> Sampler
        self.elem_states = []                 # list of (ptr, [element dicts])
        self.elem_by_ptr = {}
        self.pending_views = collections.deque()
        self.pending_samplers = collections.deque()
        self.pending_elems = collections.deque()
        self.cur_vbufs = {}                   # slot -> dict(buffer=ptr, stride, offset)
        self.cur_elems = []                   # element dicts from the bound element state
        self.cur_sampler_slots = {}           # slot -> sampler ptr
        self.cur_view_slots = {}              # slot -> view ptr
        self.fb_w = self.fb_h = None
        self.join_ambiguous = 0
        self.note_no_bytes = False
        self.buf_truncated = 0

    # -- helpers -------------------------------------------------------------------------
    def join(self, pending, table, ptr, value):
        """Pair a created object with the first pointer of its kind that has not been seen yet.

        This exists only because the dump has no return values. It is an ordering assumption and
        the report discloses it; a mismatch shows up as implausible decoded values rather than
        silently.
        """
        if ptr in table:
            return table[ptr]
        if pending:
            obj = pending.popleft()
            table[ptr] = obj
            obj.ptr = ptr
            return obj
        # A pointer appeared with no creation to pair it with: keep it unattached rather than
        # inventing a match.
        self.join_ambiguous += 1
        return None

    def store_bytes(self, ptr, offset, data):
        if not data:
            return
        if self.buf_bytes + len(data) > self.buf_cap:
            self.buf_truncated += 1
            return
        buf = self.buffers.get(ptr)
        if buf is None:
            buf = bytearray()
            self.buffers[ptr] = buf
        end = offset + len(data)
        if len(buf) < end:
            buf.extend(b"\0" * (end - len(buf)))
        buf[offset:end] = data
        self.buf_bytes += len(data)

    # -- the calls -----------------------------------------------------------------------
    def feed(self, root, call_no, detail):
        method = root.attrs.get("method", "")
        klass = root.attrs.get("class", "")
        a = Args(root)

        if klass == "pipe_context":
            if method == "buffer_subdata":
                ptrs = a.ptrs()
                blobs = a.byte_blobs()
                off = a.num("buffer_offset", 0) or 0
                data = parse_hex_blob(blobs[0]) if blobs else b""
                if ptrs and data:
                    self.store_bytes(ptrs[0], int(off), data)
                elif ptrs:
                    # A <bytes> element that is present but empty, or absent entirely: either way
                    # the vertex data is not in this trace and the coordinates cannot be read from
                    # it. Recorded so the report says why rather than just failing arithmetic.
                    self.note_no_bytes = True
            elif method in ("resource_create", "texture_create"):
                pass
            elif method == "create_sampler_view":
                t = TexObj(len(self.texobjs), call_no)
                st = a.structs("pipe_sampler_view")
                if st:
                    m = a.struct_members(st[0])
                    t.target = enum_name(TARGET, _val(m.get("target")))
                    t.fmt = _val(m.get("format")) or "?"
                    t.w = _int(_val(m.get("width")))
                    t.h = _int(_val(m.get("height")))
                    t.first_level = _int(_val(m.get("first_level")))
                    t.last_level = _int(_val(m.get("last_level")))
                    sw = [_val(m.get(k)) for k in
                          ("swizzle_r", "swizzle_g", "swizzle_b", "swizzle_a")]
                    if any(s is not None for s in sw):
                        t.swizzle = "/".join(str(s) for s in sw)
                    res = _first_ptr(m.get("texture")) or _first_ptr(m.get("resource"))
                    t.res = res or (a.ptrs()[0] if a.ptrs() else None)
                self.texobjs.append(t)
                self.pending_views.append(t)
            elif method == "set_sampler_views":
                for p in a.ptrs():
                    self.join(self.pending_views, self.views_by_ptr, p, None)
                base = a.num("start", 0) or 0
                for i, p in enumerate(a.ptrs()):
                    self.cur_view_slots[int(base) + i] = p
            elif method == "create_sampler_state":
                s = Sampler(len(self.samplers), call_no)
                st = a.structs("pipe_sampler_state")
                if st:
                    m = a.struct_members(st[0])
                    s.wrap_s = enum_name(WRAP, _val(m.get("wrap_s")))
                    s.wrap_t = enum_name(WRAP, _val(m.get("wrap_t")))
                    s.norm = _val(m.get("normalized_coords"))
                    s.minf = enum_name(FILTER, _val(m.get("min_img_filter")))
                    s.magf = enum_name(FILTER, _val(m.get("mag_img_filter")))
                    s.mipf = enum_name(MIPFILTER, _val(m.get("min_mip_filter")))
                    s.lod_bias = _val(m.get("lod_bias"))
                    s.max_aniso = _val(m.get("max_anisotropy"))
                self.samplers.append(s)
                self.pending_samplers.append(s)
            elif method == "bind_sampler_states":
                for p in a.ptrs():
                    self.join(self.pending_samplers, self.samplers_by_ptr, p, None)
                base = a.num("start", 0) or 0
                for i, p in enumerate(a.ptrs()):
                    self.cur_sampler_slots[int(base) + i] = p
            elif method == "create_vertex_elements_state":
                elems = []
                arr = a.structs("pipe_vertex_element")
                if not arr:
                    arr = _elem_structs(a)
                for st in arr:
                    m = a.struct_members(st)
                    elems.append({
                        "src_offset": _int(_val(m.get("src_offset"))) or 0,
                        "buffer": _int(_val(m.get("vertex_buffer_index"))) or 0,
                        "divisor": _int(_val(m.get("instance_divisor"))) or 0,
                        "fmt": _val(m.get("src_format")) or "?",
                    })
                self.elem_states.append(elems)
                self.pending_elems.append(elems)
            elif method == "bind_vertex_elements_state":
                ptrs = a.ptrs()
                if ptrs:
                    if ptrs[0] in self.elem_by_ptr:
                        self.cur_elems = self.elem_by_ptr[ptrs[0]]
                    elif self.pending_elems:
                        e = self.pending_elems.popleft()
                        self.elem_by_ptr[ptrs[0]] = e
                        self.cur_elems = e
                    else:
                        self.join_ambiguous += 1
            elif method == "set_vertex_buffers":
                base = a.num("start_slot", 0) or 0
                arr = a.structs("pipe_vertex_buffer")
                for i, st in enumerate(arr):
                    m = a.struct_members(st)
                    self.cur_vbufs[int(base) + i] = {
                        "buffer": _first_ptr(m.get("buffer")),
                        "stride": _int(_val(m.get("stride"))) or 0,
                        "offset": _int(_val(m.get("buffer_offset"))) or 0,
                    }
            elif method == "set_framebuffer_state":
                cbufs = a.structs("pipe_surface")
                if cbufs:
                    m = a.struct_members(cbufs[0])
                    self.fb_w = _int(_val(m.get("width"))) or self.fb_w
                    self.fb_h = _int(_val(m.get("height"))) or self.fb_h
                if self.fb_w is None:
                    t = a.num("width")
                    self.fb_w = int(t) if t else self.fb_w
                    t = a.num("height")
                    self.fb_h = int(t) if t else self.fb_h
            elif method in ("draw_vbo", "draw_elements", "draw_arrays", "draw"):
                if detail:
                    return self.describe_draw(a, call_no)
        return None

    def describe_draw(self, a, call_no):
        d = Draw()
        d.call_no = call_no
        st = a.structs("pipe_draw_info")
        if st:
            m = a.struct_members(st[0])
            d.mode = enum_name(PRIM, _val(m.get("mode")))
            d.count = _int(_val(m.get("count")))
            d.start = _int(_val(m.get("start")))
            d.indexed = _val(m.get("indexed"))
        else:
            d.mode = enum_name(PRIM, a.num("mode"))
            d.count = a.num("count")
            d.indexed = a.first("indexed")
        d.fb_w, d.fb_h = self.fb_w, self.fb_h
        for slot in sorted(self.cur_view_slots):
            p = self.cur_view_slots[slot]
            t = self.views_by_ptr.get(p)
            d.views.append((slot, p, t))
        for slot in sorted(self.cur_sampler_slots):
            p = self.cur_sampler_slots[slot]
            d.samplers.append((slot, p, self.samplers_by_ptr.get(p)))
        d.elems = list(self.cur_elems)
        d.vbufs = [self.cur_vbufs[k] for k in sorted(self.cur_vbufs)]
        d.vertices = self.decode_vertices(d)
        return d

    # -- vertex decoding -----------------------------------------------------------------
    def decode_vertices(self, d, limit=8):
        """Reconstruct the first vertices of a draw from the shadow copies of its buffers.

        No format table is consulted: the element's byte width is the distance to the next
        element's src_offset (or the stride, for the last), and the payload is read as packed
        float32. That is right for the formats this stack uses for positions and texture
        coordinates and is visibly wrong (implausible magnitudes) if it is not, which is the point
        of printing the numbers rather than a verdict alone.
        """
        if not d.elems or not d.vbufs:
            d.note = "no vertex-element/vertex-buffer state bound; cannot decode vertices"
            return None
        n = d.count if isinstance(d.count, int) else None
        if not n or n > 100000:
            d.note = f"draw count {d.count!r} not usable for vertex reconstruction"
            return None
        n = min(n, limit)
        out = []
        for vi in range(n):
            v = {}
            for ei, e in enumerate(d.elems):
                slot = e["buffer"]
                if slot >= len(d.vbufs):
                    continue
                vb = d.vbufs[slot]
                bufptr, stride = vb["buffer"], vb["stride"]
                if not bufptr or stride <= 0:
                    continue
                off = vb["offset"] + vi * stride + e["src_offset"]
                # width = space to the next element in this buffer, else to the stride end
                nxt = stride - e["src_offset"]
                for e2 in d.elems:
                    if e2 is not e and e2["buffer"] == slot:
                        delta = e2["src_offset"] - e["src_offset"]
                        if 0 < delta < nxt:
                            nxt = delta
                buf = self.buffers.get(bufptr)
                if buf is None or off + nxt > len(buf):
                    v[ei] = None
                    continue
                raw = bytes(buf[off:off + nxt])
                ncomp = nxt // 4
                if ncomp < 1:
                    v[ei] = None
                    continue
                v[ei] = (raw, [ _f32(raw, i * 4) for i in range(min(ncomp, 4)) ])
            out.append(v)
        return out


# -- tiny helpers ---------------------------------------------------------------------------


def _val(node):
    """The scalar a <member> stands for, however deeply it is wrapped.

    The dump may write a member as <member name='mode'><enum>4</enum></member> or as
    <member name='mode'><enum><int>4</int></enum></member>, and the two differ only in nesting, so
    this descends instead of assuming a shape.
    """
    if node is None:
        return None
    if node.tag == "ptr":
        return node.text
    if node.tag == "null":
        return None
    if node.tag in ("struct", "array"):
        return None
    if node.text:
        return node.text.strip()
    for n in walk(node):
        if n is not node and n.tag in ("int", "uint", "float", "bool", "enum", "string"):
            return n.text.strip() if n.text else None
    return None


def _int(v):
    if v is None:
        return None
    try:
        return int(str(v), 0)
    except ValueError:
        try:
            return int(float(v))
        except ValueError:
            return None


def _first_ptr(node):
    if node is None:
        return None
    for n in walk(node):
        if n.tag == "ptr":
            return n.text
    return None


def _elem_structs(a):
    """pipe_vertex_element may be dumped as a bare <array> of structs without the type name."""
    out = []
    for arr in a.root.kids:
        for n in walk(arr):
            if n.tag == "struct" and "src_offset" in a.struct_members(n):
                out.append(n)
    return out


def _f32(raw, off):
    import struct as _s

    if off + 4 > len(raw):
        return float("nan")
    return _s.unpack_from("<f", raw, off)[0]


# --------------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------------


# Attribute indices for the shear test, when the automatic choice has to be overridden.
_POS_ELEM = None
_TEX_ELEM = None


def fmt_f(x, nd=4):
    if x is None:
        return "?"
    try:
        if x != x:  # nan
            return "nan"
        return f"{x:.{nd}g}"
    except TypeError:
        return str(x)


def shear_test(d, expect, out):
    """Does this draw's geometry contain a du/dy of `expect` texels per scanline?

    The measured artefact is a constant lateral offset per row. On a quad, a constant offset per
    row and a constant du/dy over the quad are the same statement, so the quantity to compare with
    the measurement is the coordinate slope the vendor supplied:

        du/dy_screen = (u_bottom - u_top) / (y_bottom - y_top)     [texels of u per pixel row]
                     = that ratio times (units per pixel) times texture width

    Positions are in NDC when |y| <= 1.05 and in pixels otherwise; units-per-pixel follows from the
    framebuffer height for NDC. If no framebuffer height was recorded the raw slope is printed and
    no verdict is given, rather than inventing a scale.
    """
    if not d.vertices:
        out(f"  shear test: not computable ({d.note or 'no vertex data'})")
        return
    tex = None
    for _slot, _p, t in d.views:
        if t is not None and t.w:
            tex = t
            break
    if tex is None:
        out("  shear test: no sampler view with known dimensions is bound to this draw")
        return

    # Choose position and texcoord attributes.
    #
    # Spread alone is not a safe discriminator: a sheared quad's u range can exceed the position
    # range (it does in the sample that exposed this), which silently swapped the two and made the
    # test report a degenerate quad. Positions in this stack are vec3/vec4 and texcoords vec2, so
    # a unique attribute with three or more components wins; otherwise layout order decides, since
    # every convention puts position at the lowest offset. The mapping actually used is printed,
    # and --pos-elem/--tex-elem override it.
    cand = {}
    for v in d.vertices:
        for ei, val in v.items():
            if val is not None:
                cand.setdefault(ei, []).append(val[1])
    if len(cand) < 2:
        out(f"  shear test: only {len(cand)} attribute(s) decodable, need position and texcoord")
        return

    def ncomp(series):
        return max(len(c) for c in series)

    order = sorted(cand)
    wide = [k for k in order if ncomp(cand[k]) >= 3]
    if _POS_ELEM is not None:
        pos_i = _POS_ELEM
    elif len(wide) == 1:
        pos_i = wide[0]
    else:
        pos_i = order[0]
    if _TEX_ELEM is not None:
        tex_i = _TEX_ELEM
    else:
        tex_i = next((k for k in order if k != pos_i and ncomp(cand[k]) >= 2), None)
    if tex_i is None or pos_i not in cand or tex_i not in cand:
        out("  shear test: could not identify both a position and a texture-coordinate attribute")
        return
    out(f"  attributes: elem {pos_i} read as position ({ncomp(cand[pos_i])} comps), "
        f"elem {tex_i} as texture coordinates ({ncomp(cand[tex_i])} comps)"
        + "   [override with --pos-elem/--tex-elem]")

    pos = cand[pos_i]
    texc = cand[tex_i]
    ys = [c[1] for c in pos]
    ndc = max(abs(y) for y in ys) <= 1.05
    if ndc:
        if not d.fb_h:
            out(f"  shear test: positions look like NDC but framebuffer height is unknown; "
                f"du/dy in NDC units is not convertible to texels")
            return
        units_per_px = 2.0 / float(d.fb_h)
    else:
        units_per_px = 1.0

    # Group vertices into rows, then take the slope at a fixed x on each edge.
    #
    # Averaging u per row is wrong for triangles: the two triangles of a quad share two vertices,
    # so a plain mean weights one corner twice and understates the slope by a third (observed as
    # 2.11 where the input was exactly 3.0). Comparing rows at a fixed x is both correct and the
    # same operation as the frame measurement, which matched rows at edge positions.
    rows = {}
    tol = max(1e-4, 1e-3 * (max(ys) - min(ys)))
    for p, t in zip(pos, texc):
        rows.setdefault(round(p[1] / tol), []).append((p[0], p[1], t[0]))
    if len(rows) != 2:
        out(f"  shear test: expected 2 distinct rows, found {len(rows)} "
            f"(y values {fmt_f(min(ys), 3)}..{fmt_f(max(ys), 3)}); not a simple quad")
        return

    left, right = {}, {}
    for key, vs in rows.items():
        vs.sort(key=lambda t: t[0])
        y = sum(v[1] for v in vs) / len(vs)
        left[key] = (y, vs[0][2])
        right[key] = (y, vs[-1][2])
    keys = list(rows)

    def slope(pair):
        (ya, ua), (yb, ub) = pair
        if abs(yb - ya) < 1e-9:
            return None
        return (ub - ua) / (yb - ya)

    s_left = slope([left[keys[0]], left[keys[1]]])
    s_right = slope([right[keys[0]], right[keys[1]]])
    if s_left is None or s_right is None:
        out("  shear test: the two rows share a y value; degenerate quad")
        return
    du_dy = 0.5 * (s_left + s_right)
    y_a, ua_l = left[keys[0]]
    y_b, ub_l = left[keys[1]]

    out(f"  texture: ptr={tex.res} {tex.dims()} target={tex.target} format={tex.fmt}")
    if any(s is not None for _s, _p, s in d.samplers):
        for _slot, sp, s in d.samplers:
            if s is None:
                continue
            out(f"  sampler: wrap_s={s.wrap_s} wrap_t={s.wrap_t} "
                f"normalized_coords={s.norm} min={s.minf} mag={s.magf} mip={s.mipf}")
    out(f"  quad rows: left edge y={fmt_f(y_a, 6)} u={fmt_f(ua_l, 8)} -> "
        f"y={fmt_f(y_b, 6)} u={fmt_f(ub_l, 8)}  (positions in "
        f"{'NDC' if ndc else 'pixels'})")
    out(f"  du/dy: left edge {fmt_f(s_left, 6)}, right edge {fmt_f(s_right, 6)} u-units per "
        f"position unit")
    if abs(s_left - s_right) > 0.2 * max(abs(s_left), abs(s_right), 1e-12):
        out("  WARNING: the two edges disagree, so this is not a uniform shear; the average below "
            "is reported but should not be compared with a constant per-row offset.")
    texels_per_row = du_dy * units_per_px * float(tex.w)
    out(f"  du/dy = {fmt_f(du_dy, 6)} u-units per position unit  ->  "
        f"{fmt_f(texels_per_row, 5)} texels per pixel row")
    drop = abs(ub_l - ua_l)
    rows_count = abs(y_b - y_a) / units_per_px
    out(f"  u change across the quad at the left edge: {fmt_f(drop, 6)} "
        f"({fmt_f(drop * tex.w, 5)} texels over {fmt_f(rows_count, 6)} rows)")

    if abs(texels_per_row) <= 0.25:
        out("  VERDICT: texture coordinates are axis-aligned (du/dy ~ 0). A 3-texel-per-row "
            "shear is NOT in the coordinates.")
    elif abs(abs(texels_per_row) - expect) <= max(0.35, 0.15 * expect):
        out(f"  VERDICT: du/dy ~= {fmt_f(texels_per_row, 5)} texels/row, matching the measured "
            f"{expect:g}. The shear IS in the texture coordinates the vendor supplies.")
    else:
        out(f"  VERDICT: du/dy ~= {fmt_f(texels_per_row, 5)} texels/row, which is neither zero "
            f"nor {expect:g}; report separately.")


def report(opt):
    out = print
    path = opt.trace
    size = os.path.getsize(path)
    out(f"== trace ==\n{path}  ({size} bytes, {size / 1e6:.1f} MB)")

    hist = collections.Counter()
    replayer = Replay(opt.buffer_cap * 1024 * 1024)
    replayer.note_no_bytes = False
    draws = []
    total = 0
    saw_tail = False
    dump_wanted = set(opt.dump_call or []) | ({opt.draw} if opt.draw is not None else set())

    with open(path, "rb") as fb:
        # detect a completed trace without reading the whole file
        fb.seek(max(0, size - 4096))
        saw_tail = b"</trace>" in fb.read()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for frag in iter_call_fragments(fh):
            total += 1
            root = parse_fragment(frag)
            klass = root.attrs.get("class", "?")
            method = root.attrs.get("method", "?")
            hist[f"{klass}::{method}"] += 1
            if total in dump_wanted:
                out(f"\n== raw call {total} ==\n{frag}")
            want_detail = len(draws) < opt.max_draws
            d = replayer.feed(root, total, want_detail)
            if d is not None:
                draws.append(d)
                if opt.stop_after and len(draws) >= opt.stop_after:
                    break
            elif opt.draw is not None and total == opt.draw:
                pass

    out(f"calls: {total}" + ("" if saw_tail else "   [trace has no </trace>: truncated, expected "
                             "for a killed application]"))
    out(f"distinct methods: {len(hist)}")
    for k, v in hist.most_common(24):
        out(f"  {v:7d}  {k}")
    if hist.get("pipe_context::draw_vbo", 0) == 0 and total > 0:
        out("\n! no draw_vbo calls recorded. If the trace ends at pipe_screen::create, the "
            "application did not reach a draw before it was killed; run longer.")
    if replayer.note_no_bytes:
        out("\n! buffer_subdata calls carried no <bytes> payload, so this trace contains no vertex "
            "data: the shear test cannot read texture coordinates from it, although the texture "
            "and sampler inventories above are still valid. See the fallback in GALLIUM_TRACE.md.")

    # --- texture objects ---
    out(f"\n== texture objects (create_sampler_view): {len(replayer.texobjs)} ==")
    for t in replayer.texobjs[:40]:
        out(f"  #{t.idx:<3d} call {t.call:<6d} res={t.res or '?':<12s} {t.dims():<12s} "
            f"target={t.target:<8s} format={t.fmt}"
            + (f" levels={t.first_level}..{t.last_level}" if t.first_level is not None else "")
            + (f" swizzle={t.swizzle}" if t.swizzle else "")
            + (f" bound_as={t.ptr}" if t.ptr else "  [no pointer join]"))
    if len(replayer.texobjs) > 40:
        out(f"  ... {len(replayer.texobjs) - 40} more")

    # --- sampler states ---
    out(f"\n== sampler states (create_sampler_state): {len(replayer.samplers)} ==")
    for s in replayer.samplers[:40]:
        out(f"  #{s.idx:<3d} call {s.call:<6d} wrap_s={s.wrap_s:<18s} wrap_t={s.wrap_t:<18s} "
            f"normalized_coords={s.norm} min={s.minf} mag={s.magf} mip={s.mipf} "
            f"lod_bias={s.lod_bias}")

    # --- optional cross reference ---
    if opt.gl_log and os.path.exists(opt.gl_log):
        out(f"\n== cross-reference: {opt.gl_log} ==")
        seen = 0
        for line in open(opt.gl_log, errors="replace"):
            if "glTexImage2D" in line:
                out("  " + line.rstrip())
                seen += 1
                if seen >= 40:
                    break
        if not seen:
            out("  (no glTexImage2D lines)")

    # --- draws ---
    out(f"\n== draws (detail for {len(draws)}) ==")
    for i, d in enumerate(draws):
        out(f"\n[draw {i + 1}] call {d.call_no}  {d.mode}  count={d.count} "
            f"start={d.start} indexed={d.indexed}  fb={d.fb_w}x{d.fb_h}")
        for slot, p, t in d.views:
            if t is None:
                out(f"  view[{slot}] {p}  [unpaired pointer]")
            else:
                out(f"  view[{slot}] {p} -> texture {t.dims()} {t.target} format={t.fmt}")
        if not d.views:
            out("  view[s] none bound (untextured draw)")
        for slot, p, s in d.samplers:
            out(f"  sampler[{slot}] {p} -> "
                + (f"wrap_s={s.wrap_s} wrap_t={s.wrap_t} normalized={s.norm}" if s else
                   "[unpaired pointer]"))
        if d.elems:
            for ei, e in enumerate(d.elems):
                out(f"  elem[{ei}] buffer={e['buffer']} src_offset={e['src_offset']} "
                    f"divisor={e['divisor']} src_format={e['fmt']}")
        if d.vertices and not opt.quiet:
            for vi, v in enumerate(d.vertices[:4]):
                parts = []
                for ei in sorted(v):
                    val = v[ei]
                    if val is None:
                        parts.append(f"e{ei}=?")
                    else:
                        parts.append(f"e{ei}=[" + ", ".join(fmt_f(c, 6) for c in val[1]) + "]")
                out(f"  v{vi}: " + "  ".join(parts))
            if opt.raw:
                for ei in sorted(d.vertices[0]):
                    val = d.vertices[0][ei]
                    if val:
                        out(f"  raw e{ei}: {val[0].hex()}")
        if d.note:
            out(f"  note: {d.note}")
        shear_test(d, opt.expect_texels, out)

    out(f"\n== assumptions ==")
    out(f"  sampler-view/sampler-state joins: {replayer.join_ambiguous} unpaired pointer(s). "
        "The dump records arguments only, so created objects are matched to pointers positionally.")
    if replayer.buf_truncated:
        out(f"  {replayer.buf_truncated} buffer upload(s) skipped by --buffer-cap; raise it if "
            f"vertex data looks missing.")
    out("  attribute decoding assumes packed float32 and derives each element's width from the "
        "next element's src_offset (or the stride). Format enums are printed raw, not mapped.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("trace")
    p.add_argument("--max-draws", type=int, default=8)
    p.add_argument("--stop-after", type=int, default=0)
    p.add_argument("--draw", type=int, default=None)
    p.add_argument("--dump-call", type=int, action="append", default=[])
    p.add_argument("--gl-log", default=None)
    p.add_argument("--expect-texels", type=float, default=3.0)
    p.add_argument("--buffer-cap", type=int, default=64)
    p.add_argument("--raw", action="store_true")
    p.add_argument("--pos-elem", type=int, default=None,
                   help="element index to read as position (default: auto)")
    p.add_argument("--tex-elem", type=int, default=None,
                   help="element index to read as texture coordinates (default: auto)")
    p.add_argument("-q", "--quiet", action="store_true")
    opt = p.parse_args(argv)
    global _POS_ELEM, _TEX_ELEM
    _POS_ELEM, _TEX_ELEM = opt.pos_elem, opt.tex_elem
    if not os.path.exists(opt.trace):
        raise SystemExit(f"{opt.trace}: no such file")
    return report(opt)


if __name__ == "__main__":
    sys.exit(main())
