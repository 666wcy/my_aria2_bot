#!/bin/bash

rclone copy -v /root/Download/"${1}" "${Remote}:${Upload}"
rm -rf /root/Download/"$1"