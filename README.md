# אתר תאמר חמדאן — רואה חשבון (G.T. CPAs Office)

אתר תדמית לרואה החשבון תאמר חמדאן. עברית · ערבית · אנגלית · רוסית.

- **אתר חי:** https://cpasgt-site.web.app
- **אחסון:** Firebase Hosting (פרויקט `cpasgt-site` (חשבון tamerh@cpasgt.com))
- **פיד עדכוני מיסוי:** `scripts/fetch_updates.py` מושך מדי יום (GitHub Actions) את הפרסומים
  הרלוונטיים של רשות המסים מ-gov.il — מס הכנסה, מע"מ, דוחות שנתיים ועדכוני חקיקה —
  וכותב אותם ל-`public/data/updates.json` שמוצג באתר במדור "עדכונים מרשות המסים".

## פריסה

```bash
firebase deploy --only hosting
```
