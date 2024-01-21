#!/bin/bash
progdir=$(dirname $0)
$progdir/monitor.py -L debug -c $progdir/config/example.json $*
