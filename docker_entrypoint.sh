#!/bin/bash
set -e

if [ $# -lt 2 ]; then
  if [ $# -gt 0 ]; then
    if [ $1 -eq 'build_frontend' ]; then
      cd /app/web && npm install
      npm run build --mode=production
    fi
    exec  /app/server && \
          gunicorn \
            --workers 6 \
            --threads 4, \
            --timeout 3600 \
            --bind 0.0.0.0:5000 \
            wsgi:app
  else
    echo "Unknown command. Exiting!"
  fi
fi