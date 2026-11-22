"""Strict, lab-only parser for a disconnected VM interface inventory."""
import ipaddress
import re

_MARKERS = ('IFACES', 'FLAGS', 'ADDRS', 'ROUTE4', 'ROUTE6', 'DONE')
_SGR = re.compile(r'\x1b\[[0-9;]*m')

def parse_inventory(raw):
    """Return loopback flags and addresses; reject ambiguous or external routes."""
    raw = _SGR.sub('', raw)
    if '\x1b' in raw or '\r' in raw or '\x00' in raw:
        raise ValueError('unsupported terminal control sequence')
    sections = {}
    key = None
    for line in raw.splitlines():
        if line in _MARKERS:
            if line in sections or len(sections) != _MARKERS.index(line):
                raise ValueError('duplicate or unordered section')
            key = line
            sections[key] = []
        elif key is None:
            raise ValueError('text before inventory')
        elif line:
            sections[key].append(line)
    if tuple(sections) != _MARKERS or sections['DONE']:
        raise ValueError('incomplete inventory')
    if sections['IFACES'] != ['lo']:
        raise ValueError('non-loopback or ambiguous interface')
    if len(sections['FLAGS']) != 1:
        raise ValueError('invalid loopback flags')
    flags = int(sections['FLAGS'][0], 16)
    addresses = []
    for line in sections['ADDRS']:
        match = re.search(r'\binet\s+(\S+)', line)
        if not match or not re.search(r'^\d+:\s+lo\s', line):
            raise ValueError('unexpected address output')
        interface = ipaddress.ip_interface(match.group(1))
        if interface.version != 4 or not interface.ip.is_loopback:
            raise ValueError('non-loopback address')
        addresses.append(str(interface))
    for category in ('ROUTE4', 'ROUTE6'):
        for line in sections[category]:
            fields = line.split()
            if not fields:
                raise ValueError('empty route')
            if 'dev' in fields and (fields.index('dev') + 1 >= len(fields) or fields[fields.index('dev')+1] != 'lo'):
                raise ValueError('non-loopback route interface')
            if fields[0] in ('unreachable', 'prohibit', 'blackhole'):
                if 'via' in fields:
                    raise ValueError('route has a gateway')
                continue
            if 'dev' not in fields or 'default' in fields or 'via' in fields:
                raise ValueError('external or ambiguous route')
            dest = fields[1] if fields[0] in ('local','broadcast','anycast','multicast') else fields[0]
            net = ipaddress.ip_network(dest, strict=False)
            limit = ipaddress.ip_network('127.0.0.0/8' if net.version == 4 else '::1/128')
            if not net.subnet_of(limit) or (net.version == 4) != (category == 'ROUTE4'):
                raise ValueError('non-loopback route')
    return flags, addresses
