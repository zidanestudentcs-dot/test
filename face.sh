#!/bin/bash
# fb_page_info.sh — Kali Linux script to extract public contact info and Page ID
# Usage:
#   ./fb_page_info.sh <facebook_page_name_or_url> [GRAPH_ACCESS_TOKEN]
# Example:
#   ./fb_page_info.sh "facebook.com/RootMind" "APPID|APPSECRET"
# Notes:
#  - PAGE can be a full URL or a short name (RootMind).
#  - If you provide a Graph token the script will attempt Graph API fields.

set -euo pipefail

PAGE_RAW="$1"
ACCESS_TOKEN="${2:-}"

# Normalize input to page short name or URL path
# remove trailing slashes and protocol
PAGE_CLEAN=$(echo "$PAGE_RAW" | sed -E 's#https?://##; s#^www\.##; s#/$##')
# if input is full facebook URL like facebook.com/Name or m.facebook.com/Name
PAGE_PATH=$(echo "$PAGE_CLEAN" | awk -F'/' '{print $2?$2:$1}')

echo
echo "Target page: $PAGE_RAW"
echo "Resolved page handle/path: $PAGE_PATH"
echo

TMPDIR=$(mktemp -d)
cd "$TMPDIR" || exit 1

# 1) Try to find Page ID via graph "id by url" trick (works for many public pages)
echo "[1/4] Fetching Page metadata via graph lookup (no token)"
GRAPH_LOOKUP_URL="https://graph.facebook.com/?id=https://facebook.com/${PAGE_PATH}"
GRAPH_RAW=$(curl -s -L -A "Mozilla/5.0 (X11; Linux x86_64)" "$GRAPH_LOOKUP_URL" || true)
echo "$GRAPH_RAW" | jq . 2>/dev/null || echo "$GRAPH_RAW" | sed -n '1,6p'
PAGE_ID=$(echo "$GRAPH_RAW" | jq -r '.og_object.id // .id // empty' 2>/dev/null || true)

if [ -z "$PAGE_ID" ]; then
  echo "Page ID not found via graph lookup. Attempting fallback: parse HTML for page_id..."
  # Fetch public mobile page and try to find data-store or page ID
  curl -s -L -A "Mozilla/5.0 (X11; Linux x86_64)" "https://m.facebook.com/${PAGE_PATH}" -o page_mobile.html
  PAGE_ID=$(grep -Eo 'page_id":[0-9]+' page_mobile.html | head -n1 | sed 's/[^0-9]//g' || true)
fi

if [ -n "$PAGE_ID" ]; then
  echo "Found Page ID: $PAGE_ID"
else
  echo "Page ID not found. Some pages block public lookup or require login."
fi

# 2) Fetch mobile About page (often less JS, easier to scrape)
echo
echo "[2/4] Fetching mobile About page HTML (public fields only)"
curl -s -L -A "Mozilla/5.0 (X11; Linux x86_64)" "https://m.facebook.com/${PAGE_PATH}/about" -o page_about.html || {
  echo "Failed to fetch mobile about page. It may require login or be blocked."
}

# 3) Extract phone-like patterns and emails
echo
echo "[3/4] Extracting phone numbers and emails from About HTML (best-effort)"

# phone regex: international-ish
grep -Eo '\+?[0-9]{1,3}[[:space:]\-\.\(]?[0-9]{2,4}[[:space:]\-\.\)]?[0-9\-\s\(\)]{4,}' page_about.html 2>/dev/null | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | uniq -u | head -n 10 || true

echo
grep -Eio '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' page_about.html 2>/dev/null | uniq | head -n 10 || true

# 4) If you supplied an access token, call Graph API for structured fields
if [ -n "$ACCESS_TOKEN" ]; then
  if [ -n "$PAGE_ID" ]; then
    echo
    echo "[4/4] Querying Graph API for public fields (requires token). Page ID: $PAGE_ID"
    FIELDS="name,about,category,location,website,emails,phone,connected_instagram_account,created_time"
    curl -s "https://graph.facebook.com/v24.0/${PAGE_ID}?fields=${FIELDS}&access_token=${ACCESS_TOKEN}" | jq .
  else
    echo
    echo "[4/4] Cannot call Graph API because Page ID is unknown. You can instead try with the page username:"
    FIELDS="name,about,category,location,website,emails,phone,connected_instagram_account,created_time"
    curl -s "https://graph.facebook.com/v24.0/${PAGE_PATH}?fields=${FIELDS}&access_token=${ACCESS_TOKEN}" | jq .
  fi
else
  echo
  echo "No Graph token provided. To fetch more structured fields you can rerun with a Graph access token as the second argument."
fi

echo
echo "Done. Temp dir: $TMPDIR"
echo "If you want the script to clean up the temp files, re-run with TMP_CLEANUP=1 environment variable set."
