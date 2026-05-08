#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <github-username> [repo-name]" >&2
  exit 1
fi

username="$1"
repo_name="${2:-$(basename "$PWD")}"
origin_url="https://github.com/${username}/${repo_name}.git"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: current directory is not a git repository." >&2
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  if git remote get-url upstream >/dev/null 2>&1; then
    echo "Both origin and upstream already exist; leaving remote names unchanged."
  else
    echo "Renaming origin to upstream"
    git remote rename origin upstream
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Updating origin to ${origin_url}"
  git remote set-url origin "$origin_url"
else
  echo "Adding origin as ${origin_url}"
  git remote add origin "$origin_url"
fi

if git show-ref --verify --quiet refs/heads/main; then
  echo "Pushing main to origin/main and setting upstream tracking"
  git push -u origin main
else
  echo "Warning: local main branch not found; skipping push." >&2
fi

echo
echo "Remote summary:"
git remote -v

echo
echo "Branch summary:"
git branch -vv | sed -n '1,20p'
