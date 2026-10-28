#!/usr/bin/env python3
"""Read-only exact common-path comparison of complete EU and AUS packages."""

import hashlib
import json
import os

from pathlib import Path

EU = str(Path.home() / "Downloads/NaU/IONIQ5_EU")
AUS = str(Path.home() / "Downloads/NaU/2021_22_IONIQ_5_AU")


def inventory(root):
    result = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(base, name)
            result[os.path.relpath(path, root)] = path
    return result


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(8 * 1024 * 1024)
            if not block:
                return digest.hexdigest()
            digest.update(block)


def main():
    eu = inventory(EU)
    aus = inventory(AUS)
    common = sorted(set(eu) & set(aus))
    rows = []
    for relative in common:
        eu_size = os.path.getsize(eu[relative])
        aus_size = os.path.getsize(aus[relative])
        eu_hash = sha256(eu[relative])
        aus_hash = sha256(aus[relative])
        rows.append({
            "path": relative,
            "eu_size": eu_size,
            "aus_size": aus_size,
            "eu_sha256": eu_hash,
            "aus_sha256": aus_hash,
            "same_size": eu_size == aus_size,
            "byte_identical": eu_hash == aus_hash,
        })
    output = {
        "eu_file_count": len(eu),
        "aus_file_count": len(aus),
        "common_path_count": len(common),
        "eu_only": sorted(set(eu) - set(aus)),
        "aus_only": sorted(set(aus) - set(eu)),
        "common": rows,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
