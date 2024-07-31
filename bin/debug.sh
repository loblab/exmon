#!/bin/bash
progdir=$(cd "$(dirname "$0")" && pwd)
topdir=$(dirname "$progdir")
"$topdir/monitor.py" -L debug \
    -c "$topdir/config/debug.json" \
    "$@"
