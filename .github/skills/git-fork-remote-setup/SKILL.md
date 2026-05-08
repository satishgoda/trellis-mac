---
name: git-fork-remote-setup
description: 'Configure git remotes for a fork-based workflow. Use when you need to rename origin to upstream, add your fork as origin, and push local main to origin/main with upstream tracking. Keywords: git remote rename origin upstream, git fork setup, origin main tracking.'
argument-hint: '<github-username> [repo-name]'
user-invocable: true
---

# Git Fork Remote Setup

Set up a standard fork workflow for the current repository:
- Rename current `origin` remote to `upstream`
- Add your fork as the new `origin`
- Push local `main` to `origin/main` and set tracking

## When to Use
- You cloned upstream and now want to push to your own fork
- `origin` still points to upstream and should be switched
- You want local `main` to track `origin/main`

## Arguments
- `github-username`: required (for example: `satishgoda`)
- `repo-name`: optional (defaults to current folder name)

## Procedure
1. Confirm current remotes:
   - `git remote -v`
2. Run the helper script:
   - `bash ./.github/skills/git-fork-remote-setup/scripts/configure-remotes.sh <github-username> [repo-name]`
3. Verify final state:
   - `git remote -v`
   - `git branch -vv`

## What the Script Does
1. Detects repository name from current directory if omitted
2. Renames `origin` to `upstream` if needed
3. Creates or updates `origin` to `https://github.com/<github-username>/<repo-name>.git`
4. Pushes `main` to `origin/main` with `-u`
5. Prints remotes and branch tracking summary

## Script
- [configure-remotes.sh](./scripts/configure-remotes.sh)
