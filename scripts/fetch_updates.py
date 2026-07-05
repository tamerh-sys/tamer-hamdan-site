#!/usr/bin/env python3
"""
Fetch Israel Tax Authority publications from the gov.il open API,
keep only items relevant to a CPA audience (income tax, VAT, annual
reports, legislation updates), and write them to data/updates.json
for the site's "tax updates" feed.

Runs daily via GitHub Actions (.github/workflows/update-feed.yml).
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CONFIG_URL = "https://www.gov.il/CollectorsWebApi/client-config.js"
TAX_AUTHORITY_OFFICE_ID = "c0d8ba69-e309-4fe5-801f-855971774a90"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Topics (metaData "נושא") that make an item relevant on their own
RELEVANT_TOPICS = {"מס הכנסה", 'מע"מ', "מע״מ", "מס ערך מוסף",
                   "מיסוי מקרקעין", "דוחות מס שנתיים"}
# Title keywords that make an item relevant regardless of topic
RELEVANT_KEYWORDS = ["דוח שנתי", "דוחות שנתיים", "דו\"ח שנתי", "חקיקה",
                     "תיקון לחוק", "תיקון חוק", "החזר מס", "החזרי מס",
                     "ניכויים", "הצהרת הון", "שומה"]
# Items to always drop (job postings, tenders) — "מכרז" also matches "מכרזים"
EXCLUDE_KEYWORDS = ["מכרז", "למשרת", "דרושים"]

MAX_ITEMS = 12


def http_get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_client_id():
    js = http_get(CONFIG_URL)
    m = re.search(r'"clientId"\s*:\s*"([^"]+)"', js)
    if not m:
        sys.exit("client-config.js format changed — clientId not found")
    return m.group(1)


def get_publications(client_id, limit=60):
    url = ("https://openapi-gc.digital.gov.il/pub/cio/govil/rest/collectors/v1/"
           f"api/DataCollector/GetResults?CollectorType=reports"
           f"&officeId={TAX_AUTHORITY_OFFICE_ID}&culture=he&skip=0&limit={limit}")
    body = http_get(url, {
        "x-client-id": client_id,
        "Origin": "https://www.gov.il",
        "Referer": "https://www.gov.il/",
        "Accept": "application/json",
    })
    return json.loads(body)["results"]


def meta_titles(item, key):
    md = item.get("tags", {}).get("metaData") or {}
    return [t.get("title", "") for t in md.get(key, [])]


def promoted_type(item):
    pd = item.get("tags", {}).get("promotedMetaData") or {}
    types = [t.get("title", "") for t in pd.get("סוג", [])]
    return types[0] if types else ""


def is_relevant(item):
    title = item.get("title") or ""
    if any(k in title for k in EXCLUDE_KEYWORDS):
        return False
    topics = set(meta_titles(item, "נושא"))
    if topics & RELEVANT_TOPICS:
        return True
    return any(k in title for k in RELEVANT_KEYWORDS)


def parse_date(item):
    dates = meta_titles(item, "תאריך פרסום")
    if dates:
        try:
            return datetime.strptime(dates[0], "%d.%m.%Y").date().isoformat()
        except ValueError:
            pass
    return None


def main():
    client_id = get_client_id()
    results = get_publications(client_id)
    items = []
    for it in results:
        if not is_relevant(it):
            continue
        url = it.get("url") or ""
        items.append({
            "title": (it.get("title") or "").strip(),
            "url": url if url.startswith("http") else f"https://www.gov.il{url}",
            "date": parse_date(it),
            "topics": meta_titles(it, "נושא"),
            "type": promoted_type(it),
        })
    items.sort(key=lambda x: x["date"] or "", reverse=True)
    items = items[:MAX_ITEMS]

    out = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "רשות המסים בישראל · gov.il",
        "items": items,
    }
    out_path = Path(__file__).resolve().parent.parent / "public" / "data" / "updates.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(items)} relevant items (of {len(results)} fetched) → {out_path}")


if __name__ == "__main__":
    main()
