#!/bin/bash
set -e

if [ $# -eq 1 ]; then
  if [ $1 == 'build_frontend' ]; then
    cd /app/web
    rm -rf dist/ node_modules/
    npm ci --prefer-online --force && npm cache clean --force
    npm run build --mode=production
  elif [ $1 == 'server' ]; then
    cd  /app/server
    gunicorn \
      --name i2dc \
      --workers 6 \
      --threads 4 \
      --timeout 3600 \
      --keep-alive 3600 \
      --bind 0.0.0.0:8000 \
      --forwarded-allow-ips "*" \
      --worker-class uvicorn.workers.UvicornWorker \
      wsgi:app
  elif [ $1 == 'all' ]; then
    bash /docker_entrypoint.sh build_frontend && \
    bash /docker_entrypoint.sh server
  else
    exec $1
  
  fi
else
  exec $@

fi


      # --proxy-protocol \
      # --proxy-allow-from "*" \
