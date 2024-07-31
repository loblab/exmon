#!/bin/bash
progdir=$(cd "$(dirname "$0")" && pwd)
topdir=$(dirname "$progdir")
"$topdir/monitor.py" \
    -c "$topdir/config/host.json" \
    -c "$topdir/config/store/influx.json" \
    "$@"
