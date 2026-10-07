#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUNTIME_ROOT="${TLUMACZ_FILTER_HOST_RUNTIME_ROOT:-$ROOT/resources/okapi-runtime}"
SRC="$SCRIPT_DIR/FilterHost.java"

if [[ -z "${TLUMACZ_FILTER_STORE:-}" ]]; then
  TLUMACZ_FILTER_STORE="${XDG_CONFIG_HOME:-$HOME/.config}/tlumacz/filters"
fi
export TLUMACZ_FILTER_STORE

if [[ -z "${TLUMACZ_FILTER_SHARED_LIBS:-}" ]]; then
  TLUMACZ_FILTER_SHARED_LIBS="$RUNTIME_ROOT/lib"
fi
export TLUMACZ_FILTER_SHARED_LIBS

BUILD="${TLUMACZ_FILTER_HOST_BUILD_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/tlumacz/filter-host}"
CORE="$RUNTIME_ROOT/okapi-core-1.49.0-SNAPSHOT.jar"
LIB_DIR="${TLUMACZ_FILTER_HOST_LIB_DIR:-$RUNTIME_ROOT/lib}"

if [[ ! -d "$LIB_DIR" ]]; then
  echo "Brak lokalnego runtime Filter Host: $LIB_DIR" >&2
  exit 3
fi

mkdir -p "$BUILD"
if [[ ! -f "$BUILD/FilterHost.class" || "$SRC" -nt "$BUILD/FilterHost.class" || "$SCRIPT_DIR/FilterLoader.java" -nt "$BUILD/FilterHost.class" ]]; then
  javac -cp "$CORE:$LIB_DIR/*" -d "$BUILD" "$SCRIPT_DIR/FilterLoader.java" "$SRC"
fi

CP="$BUILD:$CORE:$LIB_DIR/*"
exec java -cp "$CP" pl.tlumacz.filterhost.FilterHost
