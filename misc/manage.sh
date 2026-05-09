#!/bin/bash

ARL_SERVICES=("arl-web" "arl-worker" "arl-worker-github" "arl-scheduler" "nginx")
INFRA_SERVICES=("mongod" "redis")

ALL_SERVICES=("${INFRA_SERVICES[@]}" "${ARL_SERVICES[@]}")

function start() {
    for svc in "${ALL_SERVICES[@]}"; do
        systemctl start "$svc"
    done
}

function stop() {
    for svc in "${ARL_SERVICES[@]}"; do
        systemctl stop "$svc"
    done
    for svc in "${INFRA_SERVICES[@]}"; do
        systemctl stop "$svc"
    done
}

function status() {
    for svc in "${ARL_SERVICES[@]}"; do
        systemctl status "$svc"
    done
    for svc in "${INFRA_SERVICES[@]}"; do
        systemctl status "$svc"
    done
}

function disable() {
    for svc in "${ALL_SERVICES[@]}"; do
        systemctl disable "$svc"
    done
}

function enable() {
    for svc in "${ALL_SERVICES[@]}"; do
        systemctl enable "$svc"
    done
}

function showLog() {
    for svc in "${ALL_SERVICES[@]}"; do
        echo "------ ${svc} server log ------"
        journalctl -n 15 --no-pager -u "$svc"
    done
}

function help() {
    echo "ARL 服务管理"
    echo "Usage: manage.sh [ stop | start | status | restart | disable | enable | log ]"
}

function restart() {
    stop
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    disable)
        disable
        ;;
    enable)
        enable
        ;;
    log)
        showLog
        ;;
    help)
        help
        ;;
    *)
        help
        ;;
esac
exit 0
