#!/bin/sh
# Reproduce the owner-access server from the retained, pinned upstream source.
set -eu
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 DROPBEAR_SOURCE BUILD_DIRECTORY" >&2
    exit 2
fi
source_dir=$(cd "$1" && pwd -P)
build_dir=$2
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
expected_revision=28216cd9af822732a1549b78621c2ea9a76a0fe5
[ "$(git -C "$source_dir" rev-parse HEAD)" = "$expected_revision" ] || {
    echo 'Dropbear source revision mismatch' >&2; exit 1;
}
[ -z "$(git -C "$source_dir" status --porcelain --untracked-files=no)" ] || {
    echo 'Dropbear source has tracked changes' >&2; exit 1;
}
mkdir -p "$build_dir"
build_dir=$(cd "$build_dir" && pwd -P)
cp "$script_dir/owner_dropbear_localoptions.h" "$build_dir/localoptions.h"
cd "$build_dir"
if [ ! -f config.status ]; then
    "$source_dir/configure" --host=x86_64-linux-musl --enable-static \
        --disable-zlib --disable-syslog --disable-shadow --disable-lastlog \
        --disable-utmp --disable-utmpx --disable-wtmp --disable-wtmpx \
        --disable-pututline --disable-pututxline
fi
make -j8 'PROGRAMS=dropbear dropbearkey scp' MULTI=1
x86_64-linux-musl-strip dropbearmulti
echo 'Built owner Dropbear 2026.94 with password/public-key auth and no forwarding.'
shasum -a 256 dropbearmulti
