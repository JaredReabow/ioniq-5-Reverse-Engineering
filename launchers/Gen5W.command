#!/bin/sh
# Finder opens .command files in Terminal.
set -eu
launcher_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec /bin/sh "$launcher_dir/start.sh" --terminal "$@"
