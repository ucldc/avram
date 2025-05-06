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
DATE=`date +%Y-%m-%d-%H`

set +u
source $HOME/venv/bin/activate
set -u
python manage.py dumpdata --output=$HOME/dbdumps/$DATE.json --natural-foreign --natural-primary

find $HOME/dbdumps/ -name "????-??-??-01.json" -mtime +32 -exec rm {} \;