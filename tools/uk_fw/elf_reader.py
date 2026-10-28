#!/usr/bin/env python3
"""Minimal read-only ELF64 section reader for the Ioniq5 kernel artifact.

Only what this task needs: section table parsing and address<->offset mapping.
No writes, no execution of the target.
"""

import struct
from typing import Dict, Iterable, List, Optional


class ElfSection:
    __slots__ = ("index", "name", "type", "flags", "addr", "offset", "size")

    def __init__(self, index, name, type_, flags, addr, offset, size):
        self.index = index
        self.name = name
        self.type = type_
        self.flags = flags
        self.addr = addr
        self.offset = offset
        self.size = size

    def __repr__(self) -> str:
        return (
            f"<ElfSection {self.name} addr=0x{self.addr:x} "
            f"off=0x{self.offset:x} size=0x{self.size:x}>"
        )


class Elf64:
    """Parsed view of an ELF64 little-endian file."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "rb") as handle:
            self.data = handle.read()
        if self.data[:4] != b"\x7fELF":
            raise ValueError("not an ELF file")
        if self.data[4] != 2:
            raise ValueError("expected ELFCLASS64")
        if self.data[5] != 1:
            raise ValueError("expected little-endian encoding")

        (self.e_shoff,) = struct.unpack_from("<Q", self.data, 0x28)
        (self.e_phentsize,) = struct.unpack_from("<H", self.data, 0x36)
        (self.e_phnum,) = struct.unpack_from("<H", self.data, 0x38)
        (self.e_shentsize,) = struct.unpack_from("<H", self.data, 0x3A)
        (self.e_shnum,) = struct.unpack_from("<H", self.data, 0x3C)
        (self.e_shstrndx,) = struct.unpack_from("<H", self.data, 0x3E)

        raw: List[tuple] = []
        for i in range(self.e_shnum):
            base = self.e_shoff + i * self.e_shentsize
            raw.append(struct.unpack_from("<IIQQQQIIQQ", self.data, base))

        strtab_off = raw[self.e_shstrndx][4]
        self.sections: List[ElfSection] = []
        for i, entry in enumerate(raw):
            name_off, type_, flags, addr, offset, size = entry[0:6]
            end = self.data.index(b"\x00", strtab_off + name_off)
            name = self.data[strtab_off + name_off : end].decode("latin-1")
            self.sections.append(
                ElfSection(i, name, type_, flags, addr, offset, size)
            )
        self.by_name: Dict[str, ElfSection] = {s.name: s for s in self.sections}

    def section(self, name: str) -> Optional[ElfSection]:
        return self.by_name.get(name)

    def section_bytes(self, name: str) -> bytes:
        section = self.section(name)
        if section is None:
            raise KeyError(name)
        return self.data[section.offset : section.offset + section.size]

    def loadable_sections(self) -> Iterable[ElfSection]:
        for section in self.sections:
            if section.flags & 0x2:  # SHF_ALLOC
                yield section

    def vaddr_to_offset(self, vaddr: int) -> Optional[int]:
        """Map a virtual address to a file offset using section extents."""
        for section in self.sections:
            if section.addr and section.flags & 0x2:
                if section.addr <= vaddr < section.addr + section.size:
                    return section.offset + (vaddr - section.addr)
        return None

    def offset_to_vaddr(self, offset: int) -> Optional[int]:
        for section in self.sections:
            if section.addr and section.flags & 0x2:
                if section.offset <= offset < section.offset + section.size:
                    return section.addr + (offset - section.offset)
        return None

    def read_vaddr(self, vaddr: int, length: int) -> Optional[bytes]:
        offset = self.vaddr_to_offset(vaddr)
        if offset is None:
            return None
        return self.data[offset : offset + length]

