#!/bin/bash
 
case "$1" in
    start)
        echo ">>> Starting services..."
	/bin/monit -c /apps/registry/.monitrc
	/bin/monit -c /apps/registry/.monitrc start all
        ;;
    restart)
        echo ">>> Reloading services..."
        /bin/monit -c /apps/registry/.monitrc restart all
        ;;
    stop)
        echo ">>> Stopping services..."
        /bin/monit -c /apps/registry/.monitrc stop all
	/bin/monit -c /apps/registry/.monitrc quit
	;;
  esac
