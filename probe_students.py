"""
Probe the new student portal at students.cuchd.in
"""
import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

urls_to_try = [
    "https://students.cuchd.in",
    "https://students.cuchd.in/",
    "https://students.cuchd.in/login",
    "https://students.cuchd.in/Login",
    "https://students.cuchd.in/Login.aspx",
    "https://students.cuchd.in/Default.aspx",
    "https://students.cuchd.in/uims/",
    "https://students.cuchd.in/UIMS/",
]

print(f"{'URL':<60} {'Status':>8} {'Notes'}")
print("-" * 120)

for url in urls_to_try:
    try:
        resp = requests.get(url, allow_redirects=False, timeout=10)
        notes = ""
        if resp.status_code in (301, 302, 303, 307, 308):
            notes = f"-> {resp.headers.get('Location', '?')}"
        elif resp.status_code == 200:
            has_form = "form" in resp.text.lower()[:5000]
            has_viewstate = "__VIEWSTATE" in resp.text
            notes = f"form={has_form}, viewstate={has_viewstate}, len={len(resp.text)}"
        print(f"{url:<60} {resp.status_code:>8} {notes}")
    except Exception as e:
        print(f"{url:<60} {'ERROR':>8} {str(e)[:60]}")

# Follow redirects from base
print("\n\n--- Following redirects from https://students.cuchd.in ---")
try:
    resp = requests.get("https://students.cuchd.in", allow_redirects=True, timeout=15)
    print(f"Final URL: {resp.url}")
    print(f"Status: {resp.status_code}")
    print(f"Redirect chain: {[(r.status_code, r.url) for r in resp.history]}")
    
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.find("title")
    print(f"Title: {title.get_text() if title else 'NO TITLE'}")
    
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})
    print(f"Has __VIEWSTATE: {viewstate is not None}")
    
    all_inputs = soup.find_all("input")
    print(f"\nInput fields ({len(all_inputs)}):")
    for inp in all_inputs:
        print(f"  name={inp.get('name')}, type={inp.get('type')}, id={inp.get('id')}")
    
    all_forms = soup.find_all("form")
    print(f"\nForms ({len(all_forms)}):")
    for form in all_forms:
        print(f"  action={form.get('action')}, method={form.get('method')}, id={form.get('id')}")
    
    # Look for buttons/links
    all_buttons = soup.find_all("button")
    print(f"\nButtons ({len(all_buttons)}):")
    for btn in all_buttons:
        print(f"  text={btn.get_text(strip=True)[:50]}, type={btn.get('type')}, id={btn.get('id')}")
    
    all_links = soup.find_all("a")
    print(f"\nLinks ({len(all_links)}):")
    for a in all_links[:20]:
        print(f"  href={a.get('href')}, text={a.get_text(strip=True)[:50]}")
    
    # Check for API endpoints in scripts
    scripts = soup.find_all("script")
    print(f"\nScripts ({len(scripts)}):")
    for s in scripts:
        src = s.get("src", "")
        if src:
            print(f"  src={src}")
        elif s.string:
            # look for URLs/fetch/ajax/api calls
            text = s.string[:500]
            if any(kw in text.lower() for kw in ["url", "api", "fetch", "ajax", "login", "auth"]):
                print(f"  inline (relevant): {text[:200]}")
    
    print(f"\n\nFull HTML ({len(resp.text)} chars):")
    print(resp.text[:5000])
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
