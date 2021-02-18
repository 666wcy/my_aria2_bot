#!/bin/bash


touch /root/.aria2/aria2.session
chmod 0777 /root/.aria2/ -R
chmod 0777 /bot/ -R
mkdir /.config/
mkdir /.config/rclone
touch /.config/rclone/rclone.conf
echo "$Rclone" >>/.config/rclone/rclone.conf
wget git.io/tracker.sh
chmod 0777 /tracker.sh
/bin/bash tracker.sh "/root/.aria2/aria2.conf"

nohup aria2c --conf-path=/root/.aria2/aria2.conf --rpc-listen-port=$PORT --rpc-secret=$Secret &
python3 /bot/main.py
