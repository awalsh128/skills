#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# Written here because the repo's format check rejects a file of invalid JSON.
mkdir -p services/mailer
printf '{ "name": "mail", "port": "8002",\n' > services/mailer/service.json
