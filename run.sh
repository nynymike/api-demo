#!/bin/sh

export REQUESTS_CA_BUNDLE=/var/www/html/api-demo/certs.pem
/usr/bin/python3 gg-web.py
