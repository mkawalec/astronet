#!/bin/bash
uwsgi -s /tmp/uwsgi.sock --module astronet --callable app -p 4 --stats :8251 --reload-on-as 150 --reload-on-exception --max-requests 5000
