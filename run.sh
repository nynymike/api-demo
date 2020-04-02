#!/bin/sh

export REQUESTS_CA_BUNDLE=/var/www/html/api-demo/certs.pem
/usr/bin/python3 /var/www/html/api-demo/gg-test.py

