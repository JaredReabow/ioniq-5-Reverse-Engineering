"""Plan and verify only loopback changes in an isolated VM."""

def _validate_addresses(addresses):
    if len(addresses) > 1 or any(item != '127.0.0.1/8' for item in addresses):
        raise ValueError('conflicting or duplicate loopback address')

def setup_loopback(inventory, run_command):
    """Recheck state after link-up and only add the missing loopback address."""
    flags, addresses = inventory('before')
    _validate_addresses(addresses)
    if not flags & 1:
        run_command('/sbin/ip link set dev lo up')
        flags, addresses = inventory('after-link')
        _validate_addresses(addresses)
        if not flags & 1:
            raise ValueError('loopback did not become up')
    if '127.0.0.1/8' not in addresses:
        run_command('/sbin/ip addr add 127.0.0.1/8 dev lo')
    flags, addresses = inventory('after')
    _validate_addresses(addresses)
    if not flags & 1 or addresses != ['127.0.0.1/8']:
        raise ValueError('final loopback state is incomplete')
    return flags, addresses
