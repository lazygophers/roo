#!/usr/bin/env sh
if [ -z "$husky_skip_init" ]; then
  debug () {
    if [ "$HUSKY_DEBUG" = "1" ]; then
      echo "husky (debug) - $1"
    fi
  }

  readonly hook_name="$(basename "$1")"
  debug "starting $hook_name..."

  if [ "$hook_name" = "pre-commit" ]; then
    for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|jsx|ts|tsx)$'); do
      debug "checking file: $file"
      if ! npx eslint --fix "$file" >/dev/null 2>&1; then
        echo "ESLint failed on $file"
        exit 1
      fi
      if ! npx prettier --write "$file" >/dev/null 2>&1; then
        echo "Prettier failed on $file"
        exit 1
      fi
      git add "$file"
    done
  fi

  debug "$hook_name finished"
fi
