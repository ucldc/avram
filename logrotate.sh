#!/bin/env bash

if [[ -n "$DEBUG" ]]; then 
  set -x
fi
set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value


HTTP_LOGS=~/servers/mod_wsgi-express/logs

# guess these could go in the rake file
# remove older log files
find "$HTTP_LOGS" \( -name "access.????.??.??.gz" -o -name "error.????.??.??.gz" -o -name "response-time.????.??.??.gz" -o -name "ssl_access_log.????.??.??.gz" -o -name "ssl_request_log.????.??.??.gz" \) -mtime +32 -exec rm {} \;

# compress files older than 2 weeks
find "$HTTP_LOGS" -type f -name "*.????.??.??"  -mtime +16 -exec gzip {} \;
