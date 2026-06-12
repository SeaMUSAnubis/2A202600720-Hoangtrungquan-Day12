#!/bin/sh
envsubst '${BACKEND_HOST} ${FRONTEND_HOST}' < /nginx.conf.template > /etc/nginx/nginx.conf
exec nginx -g 'daemon off;'
