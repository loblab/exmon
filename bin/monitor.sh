#!/bin/bash
progdir=$(cd "$(dirname "$0")" && pwd)
topdir=$(dirname "$progdir")
"$topdir/monitor.py" -L debug \
    -c "$topdir/config/example.json" \
    -c "$topdir/config/source/container.json" \
    -c "$topdir/config/source/host.json" \
    -c "$topdir/config/store/jsondir.json" \
    "$@"
