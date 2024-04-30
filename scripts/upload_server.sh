#!/bin/bash
sudo rsync -rav -e ssh \
 --include='*.[py|json|md|ini|txt]' --exclude='venv' --exclude='__pycache__' --exclude='cache' --exclude='.idea' \
  /mnt/c/users/nirch/pycharmprojects/pipes/server \
  root@nirush.me:/home/pipes/src