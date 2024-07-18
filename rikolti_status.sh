#!/usr/bin/env bash

if [[ -n "$DEBUG" ]]; then 
  set -x
fi

set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # http://stackoverflow.com/questions/59895
cd $DIR

set +u
source $HOME/python/bin/activate
set -u

# run python manage.py rikolti_status every 20 seconds
i=0
while [ $i -lt 3 ]; do # 3 twenty-second intervals in 1 minute
  python manage.py rikolti_status & 
  sleep 20
  i=$(( i + 1 ))
done
