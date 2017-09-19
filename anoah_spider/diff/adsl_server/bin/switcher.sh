#!/bin/bash

source /etc/profile
source /etc/bashrc

PROXY_NAME="adsl_proxy_000"

LOG="switcher.log"

function logging()
{
    echo `date "+%Y-%m-%d %H:%M:%S "` "$1" >> $LOG
}


function restart_adsl()
{
    adsl-stop
    adsl-start
}


while [ 1 == 1 ]
    do
        logging "[start]"

        restart_adsl

        new_ip=`ifconfig | grep ppp0 -A 1 | grep -oP "(net |inet addr:)\K[\d.]+(?= )"`

        logging $new_ip
        redis-cli -a "[_I_am_MONKEYKING_]" -h "123.56.168.173" -p "7988" "hset" "proxies" "$PROXY_NAME" "$new_ip"
        echo $new_ip

        sleep 120

    done
