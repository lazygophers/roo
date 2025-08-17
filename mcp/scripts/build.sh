#!/bin/bash
# This script compiles the Python application into a standalone executable using Nuitka.
set -e

# Define cache directory using XDG_CACHE_HOME or a local default
export CACHE_DIR=".nuitka-cache"
export CCACHE_DIR="$CACHE_DIR/ccache"
export PATH="/usr/lib/ccache:$PATH"

# Ensure cache directories exist
mkdir -p "$CCACHE_DIR"
mkdir -p "$CACHE_DIR/nuitka"


# Run Nuitka compilation
uv run nuitka \
    --mode=onefile \
    --assume-yes-for-downloads \
    --remove-output \
    --output-dir=build \
    --output-filename=lazygopher \
    --show-progress \
    --static-libpython=auto \
    --deployment \
    --prefer-source-code \
    --enable-plugins=anti-bloat \
    --noinclude-setuptools-mode=nofollow \
    --noinclude-pytest-mode=nofollow \
    --jobs=-1 \
    --onefile-cache-mode=cached \
    --nofollow-import-to=cryptography.* \
    --noinclude-data-files=cryptography \
    main.py

