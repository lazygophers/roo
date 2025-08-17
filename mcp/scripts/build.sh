#!/bin/bash
# This script compiles the Python application into a standalone executable using Nuitka.
set -e

# Run Nuitka compilation
uv run nuitka \
    --mode=onefile \
    --assume-yes-for-downloads \
    --output-dir=build\
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

