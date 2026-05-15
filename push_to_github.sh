#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# push_to_github.sh — Create GitHub repo & push UMKM Autopilot
# Usage: bash push_to_github.sh <GITHUB_USERNAME> <GITHUB_TOKEN> [TEAM_NAME]
# ─────────────────────────────────────────────────────────────────────────────
set -e

GITHUB_USER="${1:?Usage: bash push_to_github.sh <username> <token> [team_name]}"
GITHUB_TOKEN="${2:?Usage: bash push_to_github.sh <username> <token> [team_name]}"
TEAM_NAME="${3:-NamaTim}"

REPO_NAME="OpenClaw2026_${TEAM_NAME}_UMKMAutopilot"
API="https://api.github.com"

echo "──────────────────────────────────────────────"
echo "  Creating GitHub repo: ${GITHUB_USER}/${REPO_NAME}"
echo "──────────────────────────────────────────────"

# 1. Create repository via GitHub API
HTTP_STATUS=$(curl -s -o /tmp/gh_response.json -w "%{http_code}" \
  -X POST "${API}/user/repos" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -d "{
    \"name\": \"${REPO_NAME}\",
    \"description\": \"🤖 UMKM Autopilot — Autonomous Business OS for Indonesian SMEs | OpenClaw Agenthon 2026\",
    \"private\": false,
    \"auto_init\": false,
    \"has_issues\": true,
    \"has_projects\": false,
    \"has_wiki\": false
  }")

if [ "$HTTP_STATUS" -eq 201 ]; then
  echo "✅ Repository created successfully!"
elif [ "$HTTP_STATUS" -eq 422 ]; then
  echo "⚠️  Repository may already exist — proceeding with push..."
else
  echo "❌ Failed to create repo (HTTP $HTTP_STATUS):"
  cat /tmp/gh_response.json
  exit 1
fi

# 2. Add remote & push
REMOTE_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

git remote remove origin 2>/dev/null || true
git remote add origin "${REMOTE_URL}"
git branch -M main
git push -u origin main

echo ""
echo "──────────────────────────────────────────────"
echo "  ✅ Done! Repository live at:"
echo "  https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo "──────────────────────────────────────────────"
