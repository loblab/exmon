#!/bin/bash
progdir=$(dirname $0)
$progdir/monitor.py -L debug \
    -c $progdir/config/example.json \
    -c $progdir/config/source/container.json \
    -c $progdir/config/source/host.json \
    -c $progdir/config/store/jsondir.json \
    $@
