#!/bin/bash
# פריסה מלאה של אתר תאמר חמדאן: GitHub (חשבון tamerh-sys) + Firebase Hosting
# שימוש: ./deploy.sh "הודעת קומיט"
set -e
cd "$(dirname "$0")"

MSG="${1:-עדכון אתר}"

# קומיט אם יש שינויים
git add -A
git diff --cached --quiet || git commit -m "$MSG"

# דחיפה ל-GitHub עם החשבון של תאמר, והחזרת החשבון של סאמר מיד אחרי
gh auth switch -h github.com -u tamerh-sys
trap 'gh auth switch -h github.com -u samer92safe-ctrl' EXIT
git push
gh auth switch -h github.com -u samer92safe-ctrl
trap - EXIT

# פריסה ל-Firebase
firebase deploy --only hosting

echo "✅ נפרס: https://tamer-hamdan-site.web.app"
