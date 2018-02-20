#!/bin/bash

# Mark all created and modified variables as exported while sourcing
# the env file.
set -a
. ./env || exit 1
set +a

if [ -z "${CHAOS_EMAIL}" ]; then
    echo "No CHAOS_EMAIL set in environment"
    exit 2
fi

if [ -z "${CHAOS_PASSWORD}" ]; then
    echo "No CHAOS_PASSWORD set in environment"
    exit 4
fi

SERVICE_ACCOUNT=service-account-key.json
if [ ! -r "${SERVICE_ACCOUNT}" ]; then
    echo "Missing \"${SERVICE_ACCOUNT}\" file."
    echo "Create one with \`gcloud iam service-accounts keys create ${SERVICE_ACCOUNT} --iam-account=dka-report@dr-danskkulturarv.iam.gserviceaccount.com\`."
   exit 8
fi

d=$(date +%Y-%m)
python3 ./published_between.py 1970-01-01T12:00:00Z 2030-12-30T12:00:00Z "./dr-reports/$d.csv"

# We need to launch dbus to silence warnings from ssconvert (it will
# actually work without dbus but we don't want to get confused by
# warnings)
export $(dbus-launch)
ssconvert "./dr-reports/$d.csv" "./dr-reports/$d.xlsx"

# Cleanup dbus
kill "$DBUS_SESSION_BUS_PID"
