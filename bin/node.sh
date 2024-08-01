#!/bin/bash
progdir=$(cd "$(dirname "$0")" && pwd)
topdir=$(dirname "$progdir")
"$topdir/monitor.py" \
    -c "$topdir/config/global.json" \
    -c "$topdir/config/source/host.json" \
    -c "$topdir/config/source/redis.json" \
    -c "$topdir/config/store/influx.json" \
    "$@"
