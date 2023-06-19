#!/bin/sh
python3 -u app.py &
nginx -g 'daemon off;'
