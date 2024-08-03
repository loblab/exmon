#!/bin/bash

function config() {
    PROG_DIR=$(cd "$(dirname "$0")" && pwd)
    TOP_DIR=$(dirname "$PROG_DIR")
    SERVICE_DIR=/lib/systemd/system
    SERVICE_NAME=exmon
    TARGET_DIR=/usr/local/loblab/exmon
    RSYNC="rsync -z -auv --delete --exclude .git --exclude .*.swp --exclude __pycache__"
    if test $# -eq 0; then
        TARGET_HOST=""
        RSYNC_HOST=""
        RUN=""
        echo "Install to localhost"
    else
        TARGET_HOST=$1
        RSYNC_HOST=$TARGET_HOST:
        RUN="ssh $TARGET_HOST"
        echo "Install to $TARGET_HOST"
    fi
}

function copy_files() {
    $RUN sudo mkdir -p $TARGET_DIR
    $RUN sudo chown '$USER' $TARGET_DIR
    cd "$TOP_DIR" || return 0
    $RSYNC $TOP_DIR/ $RSYNC_HOST$TARGET_DIR/
    $RUN tree -L 2 -d $TARGET_DIR
}

function install_service() {
    local now
    echo "Install service $SERVICE_NAME ..."
    $RUN sudo cp $TARGET_DIR/config/$SERVICE_NAME.service $SERVICE_DIR/
    now=$(date '+%m/%d/%Y\ %H:%M:%S')
    $RUN sudo sed -i "s#_TIME_#$now#" $SERVICE_DIR/$SERVICE_NAME.service
    $RUN sudo systemctl daemon-reload
    $RUN sudo systemctl enable $SERVICE_NAME
    $RUN sudo systemctl restart $SERVICE_NAME
    $RUN systemctl status $SERVICE_NAME | head -n 19
    echo "Install service $SERVICE_NAME ... done"
}

function main() {
    config "$@"
    copy_files
    install_service
}

main "$@"
