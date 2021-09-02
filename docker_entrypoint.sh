#!/bin/bash
set -e

if [ $# -eq 1 ]; then
  if [ $1 == 'build_frontend' ]; then
    cd /app/web
    npm install && npm cache clean
    npm run build --mode=production
  elif [ $1 == 'server' ]; then
    cd  /app/server
    gunicorn \
      --name i2dc \
      --workers 6 \
      --threads 4 \
      --timeout 3600 \
      --bind 0.0.0.0:12115 \
      wsgi:app
  else
    exec $1
  
  fi
else
  exec $@

fi