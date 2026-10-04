#!/bin/sh
set -eu

echo "Applying database migrations..."
uv run --no-sync manage.py migrate --noinput

set +e
uv run --no-sync manage.py superuser_exists
superuser_status=$?
set -e

case "$superuser_status" in
    0)
        ;;
    10)
        echo "Configured superuser not found; running first-time configuration..."
        sh ./first_run.sh
        ;;
    *)
        exit "$superuser_status"
        ;;
esac

exec "$@"
