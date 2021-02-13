#!/bin/bash

rclone copy -P /root/Download/"${1}" "${Remote}:${Upload}"
rm -rf /root/Download/"$1"