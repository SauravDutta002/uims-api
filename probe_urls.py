"""
Probe different UIMS URLs to find the working login page.
"""
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

urls_to_try = [
    "https://uims.cuchd.in",
    "https://uims.cuchd.in/",
    "https://uims.cuchd.in/uims/",
    "https://uims.cuchd.in/UIMS/",
    "https://uims.cuchd.in/uims/login.aspx",
    "https://uims.cuchd.in/UIMS/login.aspx",
    "https://uims.cuchd.in/uims/default.aspx",
    "https://uims.cuchd.in/UIMS/default.aspx",
    "https://uims.cuchd.in/uims/Home.aspx",
    "https://uims.cuchd.in/UIMS/Home.aspx",
    "https://uims.cuchd.in/login",
    "https://uims.cuchd.in/Login",
    "https://uims.cuchd.in/Login.aspx",
    "https://uims.cuchd.in/Default.aspx",
    "https://uims.cuchd.in/home",
    "https://uims.cuchd.in/Home.aspx",
    "https://uims.cuchd.in/uims/frmLogin.aspx",
    "https://uims.cuchd.in/UIMS/frmLogin.aspx",
    "https://uims.cuchd.in/uims/frmLoginNew.aspx",
    "https://uims.cuchd.in/UIMS/frmLoginNew.aspx",
]

print(f"{'URL':<60} {'Status':>8} {'Redirect/Notes'}")
print("-" * 110)

for url in urls_to_try:
    try:
        resp = requests.get(url, allow_redirects=False, timeout=10)
        redirect = ""
        if resp.status_code in (301, 302, 303, 307, 308):
            redirect = f"-> {resp.headers.get('Location', '?')}"
        elif resp.status_code == 200:
            # Check if it has a form
            has_form = "form" in resp.text.lower()[:5000]
            has_viewstate = "__VIEWSTATE" in resp.text
            redirect = f"has_form={has_form}, has_viewstate={has_viewstate}, len={len(resp.text)}"
        print(f"{url:<60} {resp.status_code:>8} {redirect}")
    except Exception as e:
        print(f"{url:<60} {'ERROR':>8} {str(e)[:50]}")

# Also try with redirects followed for the base URL
print("\n\n--- Following redirects from base URL ---")
resp = requests.get("https://uims.cuchd.in", allow_redirects=True, timeout=10)
print(f"Final URL: {resp.url}")
print(f"Status: {resp.status_code}")
print(f"Redirect chain: {[(r.status_code, r.url) for r in resp.history]}")
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, "html.parser")
title = soup.find("title")
print(f"Title: {title.get_text() if title else 'NO TITLE'}")
viewstate = soup.find("input", {"name": "__VIEWSTATE"})
print(f"Has __VIEWSTATE: {viewstate is not None}")
all_inputs = soup.find_all("input")
print(f"Input fields ({len(all_inputs)}):")
for inp in all_inputs:
    print(f"  name={inp.get('name')}, type={inp.get('type')}")
print(f"\nHTML (first 3000 chars):\n{resp.text[:3000]}")
