#!/bin/bash
# Build once during installation, never during arming or boot. Preserve source
# and build output so the installed LGPL helper can be recreated and inspected.
set -euo pipefail

nbdfuse_build_require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        printf 'Missing build dependency: %s\n' "$1" >&2
        exit 2
    }
}

nbdfuse_build_main() {
    local helper_version='ioniq-nbdfuse-direct 1.14.2-ioniq-direct.1'
    if [[ ${1:-} == --helper-version && $# -eq 1 ]]; then
        printf '%s\n' "$helper_version"
        return
    fi
    if [[ $# -ne 1 || $1 != /* || $1 == / || -e $1 || -L $1 ]]; then
        printf 'usage: %s <new-absolute-build-directory>\nExisting builds are preserved.\n' "$0" >&2
        exit 2
    fi
    local build_dir=$1
    local script_dir
    script_dir=$(cd -- "$(dirname -- "$0")" && pwd -P)
    local patch_file="$script_dir/ioniq-nbdfuse-direct.patch"
    [[ -f $patch_file && ! -L $patch_file ]] || {
        printf 'Pinned direct-I/O patch is missing.\n' >&2; exit 2;
    }
    local command
    for command in curl sha256sum tar patch pkg-config gcc readelf python3; do
        nbdfuse_build_require_command "$command"
    done
    pkg-config --exists libnbd fuse3
    printf 'IONIQ direct-I/O helper builder 1.0.0\n'
    mkdir -m 0700 -- "$build_dir"
    local archive="$build_dir/libnbd-1.14.2.tar.gz"
    local source_dir="$build_dir/libnbd-1.14.2"
    local output="$build_dir/ioniq-nbdfuse-direct"
    curl --fail --location --silent --show-error --proto '=https' --tlsv1.2 \
        'https://download.libguestfs.org/libnbd/1.14-stable/libnbd-1.14.2.tar.gz' \
        --output "$archive"
    printf '%s  %s\n' \
        '83cc3a88d63b17353275ff4c7c8dcc778437f48ca5d51caa76da415981a7a0cf' \
        "$archive" | sha256sum --check --status
    tar -xzf "$archive" -C "$build_dir"
    [[ $(grep -Fxc 'nbdfuse_open (const char *path, struct fuse_file_info *fi)' \
        "$source_dir/fuse/operations.c") -eq 1 ]]
    patch --batch --forward --fuzz=0 -d "$source_dir" -p1 --dry-run <"$patch_file"
    patch --batch --forward --fuzz=0 -d "$source_dir" -p1 <"$patch_file"
    cp -p -- "$patch_file" "$build_dir/ioniq-nbdfuse-direct.patch"
    [[ $(grep -Fxc '  fi->direct_io = 1;' "$source_dir/fuse/operations.c") -eq 1 ]]
    [[ $(grep -Fxc '  fi->keep_cache = 0;' "$source_dir/fuse/operations.c") -eq 1 ]]
    (
        cd -- "$source_dir"
        ./configure --without-libxml2 --without-gnutls --disable-ocaml \
            --disable-python --disable-golang
    )
    local -a compile_flags link_flags
    read -r -a compile_flags <<<"$(pkg-config --cflags libnbd fuse3)"
    read -r -a link_flags <<<"$(pkg-config --libs libnbd fuse3)"
    gcc -std=gnu11 -O2 -g -Wall -Wextra -D_FILE_OFFSET_BITS=64 \
        -I"$source_dir" -I"$source_dir/include" -I"$source_dir/common/include" \
        -I"$source_dir/common/utils" -I"$source_dir/fuse" \
        "${compile_flags[@]}" \
        "$source_dir/fuse/nbdfuse.c" "$source_dir/fuse/operations.c" \
        "$source_dir/common/utils/vector.c" "$source_dir/common/utils/version.c" \
        "${link_flags[@]}" -pthread -o "$output"
    local version options symbols
    version=$("$output" --version)
    [[ ${version%%$'\n'*} == "$helper_version" ]]
    options=$("$output" --short-options)
    printf '%s\n' "$options" | grep -Fx -- '-C' >/dev/null
    printf '%s\n' "$options" | grep -Fx -- '-r' >/dev/null
    printf '%s\n' "$options" | grep -Fx -- '-s' >/dev/null
    symbols=$(readelf -Ws "$output")
    [[ $symbols == *' nbd_connect_tcp'* && $symbols == *' fuse_mount'* ]]
    printf '%s\nBuilt: %s\n' "$version" "$output"
    sha256sum "$output"
}

nbdfuse_build_main "$@"
