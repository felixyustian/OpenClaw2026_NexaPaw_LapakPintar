#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# update_for_railway.sh
# Run this from the root of your local repo clone, then push.
# Usage: bash update_for_railway.sh <LIVE_URL> <YOUTUBE_URL>
# Example:
#   bash update_for_railway.sh \
#     "https://lapakpintar.up.railway.app" \
#     "https://youtu.be/XXXXXXX"
# ─────────────────────────────────────────────────────────────────────────────
set -e

LIVE_URL="${1:?Provide live URL as first arg}"
YT_URL="${2:?Provide YouTube URL as second arg}"

echo "Updating README placeholders..."

# Replace demo video placeholder
sed -i "s|📹 Demo Video: \[https://www.youtube.com/watch?v=n798nMT8Ce0\]|📹 Demo Video: [Watch on YouTube](${YT_URL})|g" README.md

# Replace live demo placeholder
sed -i "s|🌐 Live Demo: \[https://openclaw2026nexapawlapakpintar-production.up.railway.app/docs/\]|🌐 Live Demo: [LapakPintar Live](${LIVE_URL})|g" README.md

echo "Copying Railway config files..."
cp Dockerfile.railway Dockerfile.railway   # already in place if you cloned this script
# railway.toml and Dockerfile.railway should already be in repo root

git add README.md railway.toml Dockerfile.railway
git commit -m "feat: add Railway deployment + update live demo & video links

- Add railway.toml for one-click Railway deploy
- Add Dockerfile.railway (slim, no Playwright) for Railway single-container
- Update README: live demo → ${LIVE_URL}
- Update README: demo video → ${YT_URL}"

git push origin main

echo ""
echo "✅ Done! README updated and pushed."
echo "   Live Demo : ${LIVE_URL}"
echo "   Video     : ${YT_URL}"
