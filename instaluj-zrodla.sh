#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
python3 -m pip install .
python3 -c 'from tlumacz.user_config import initialize_user_config; print(initialize_user_config())'
