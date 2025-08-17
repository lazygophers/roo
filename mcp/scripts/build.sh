#!/bin/bash
# This script compiles the Python application into a standalone executable using Nuitka.
set -e

# Explicitly set and export the ccache directory to ensure it's used.
export CCACHE_DIR=/root/.ccache
export PATH="/usr/lib/ccache:$PATH"

# Clean up previous build artifacts
rm -rf build/lazygopher


# Run Nuitka compilation
uv run nuitka \
    --mode=onefile \
    --assume-yes-for-downloads \
    --lto=yes \
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


# Move the final executable to the root directory
mv build/lazygopher .