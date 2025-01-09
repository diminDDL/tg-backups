#!/bin/sh
rm -r /mnt/tmp/*
sudo -u pi bash -c "cd /home/pi/tg-backups && /usr/bin/python3 ./single-zip.py ./config.ini"

