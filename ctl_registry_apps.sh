#!/bin/bash

source /apps/registry/venv/bin/activate

case "$1" in
    start)
        echo ">>> Starting services..."
        /usr/local/bin/monit -c /apps/registry/.monitrc
        echo "Waiting for Monit to start..."
        sleep 3
        /usr/local/bin/monit -c /apps/registry/.monitrc start all
        ;;
    restart)
        echo ">>> Reloading services..."
        /usr/local/bin/monit -c /apps/registry/.monitrc restart all
        ;;
    stop)
        echo ">>> Stopping services..."
        /usr/local/bin/monit -c /apps/registry/.monitrc stop all
        /usr/local/bin/monit -c /apps/registry/.monitrc quit
    ;;
  esac
