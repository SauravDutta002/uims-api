"""
Debug: check what the UIMS login page returns
"""
import requests
from bs4 import BeautifulSoup
import sys
import io

# Fix encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://uims.cuchd.in"
AUTHENTICATE_URL = BASE_URL + "/uims/"

print("=" * 60)
print("  Step 1: GET the login page")
print("=" * 60)

response = requests.get(AUTHENTICATE_URL, allow_redirects=True)
print(f"Status Code: {response.status_code}")
print(f"Final URL: {response.url}")
print(f"Headers: {dict(response.headers)}")
print(f"\nResponse length: {len(response.text)} chars")

# Check for redirects
print(f"\nHistory (redirects): {[r.status_code for r in response.history]}")
if response.history:
    for r in response.history:
        print(f"  {r.status_code} -> {r.url}")

soup = BeautifulSoup(response.text, "html.parser")

# Check for __VIEWSTATE
viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
print(f"\n__VIEWSTATE found: {viewstate_tag is not None}")
if viewstate_tag:
    print(f"__VIEWSTATE value (first 100 chars): {viewstate_tag['value'][:100]}")

# Check for other form fields
all_inputs = soup.find_all("input")
print(f"\nAll input fields found ({len(all_inputs)}):")
for inp in all_inputs:
    name = inp.get("name", "NO_NAME")
    itype = inp.get("type", "NO_TYPE")
    val = inp.get("value", "")[:50]
    print(f"  name={name}, type={itype}, value={val}")

# Check for forms
all_forms = soup.find_all("form")
print(f"\nAll forms found ({len(all_forms)}):")
for form in all_forms:
    print(f"  action={form.get('action')}, method={form.get('method')}")

# Print first 2000 chars of HTML to understand the page structure
print("\n" + "=" * 60)
print("  First 2000 chars of HTML")
print("=" * 60)
print(response.text[:2000])

# Check title
title = soup.find("title")
print(f"\nPage title: {title.get_text() if title else 'NO TITLE'}")
