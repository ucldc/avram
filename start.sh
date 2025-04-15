#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Starting Apache"
/apps/registry/servers/mod_wsgi-express/apachectl -D FOREGROUND

# mod_wsgi-express start-server /app/avram/collection_registry/wsgi.py \
#     --user registry \
#     --group registry \
#     --port 8000 \
#     --log-to-terminal \
#     --log-level info

