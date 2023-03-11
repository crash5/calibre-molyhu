#!/usr/bin/env bash
set -e

function toAbsolutePath {
    local target="$1"

    if [ "$target" == "." ]; then
        echo "$(pwd)"
    elif [ "$target" == ".." ]; then
        echo "$(dirname "$(pwd)")"
    else
        echo "$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
    fi
}

readonly SOURCE_PATH=$(toAbsolutePath "${1}")
readonly OUTPUT_FILE=$(toAbsolutePath ${2:-"Moly_hu_Reloaded.zip"})

if [[ ${#@} -lt 1 ]]; then
    echo "Usage: ${0} <source repo path> [output file]"
    exit
fi

readonly TEMPORARY_WORK_DIR=$(mktemp -d -p .)
cd "${TEMPORARY_WORK_DIR}"

cp "${SOURCE_PATH}"/src/calibre_plugin/__init__.py .
cp "${SOURCE_PATH}"/src/calibre_plugin/plugin-import-name-moly_hu_reloaded.txt .
cp "${SOURCE_PATH}"/src/moly_hu/moly_hu.py .
cp "${SOURCE_PATH}"/README.md .
zip -r "${OUTPUT_FILE}" .

cd ..
rm -rf "${TEMPORARY_WORK_DIR}"
