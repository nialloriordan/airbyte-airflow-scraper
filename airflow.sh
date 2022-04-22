#!/usr/bin/env bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -euo pipefail

export COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yaml"
exec docker-compose run --rm -e CONNECTION_CHECK_MAX_COUNT=0 airflow-worker "${@}"
