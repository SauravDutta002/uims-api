"""
Analyze the captcha mechanism on the CUIMS login page.
Check if the captcha image is an ASP.NET handler or if the captcha value is embedded somewhere.
"""
import requests
from bs4 import BeautifulSoup
import re
import sys
import io
import base64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

UID = "24BCS10029"
BASE_URL = "https://students.cuchd.in"

session = requests.Session()

# Step 1: GET login page
response = session.get(BASE_URL + "/")
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Submit UID
viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
viewstate_gen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})

data = {}
if viewstate_tag: data["__VIEWSTATE"] = viewstate_tag["value"]
if viewstate_gen: data["__VIEWSTATEGENERATOR"] = viewstate_gen["value"]
data["txtUserId"] = UID
data["btnNext"] = "NEXT"

response = session.post(BASE_URL + "/", data=data, allow_redirects=False)
password_url = BASE_URL + response.headers.get("Location", "")

# Step 3: GET password page
response = session.get(password_url)
soup = BeautifulSoup(response.text, "html.parser")

print("=" * 80)
print("  CAPTCHA ANALYSIS")
print("=" * 80)

# Find all images
imgs = soup.find_all("img")
print(f"\nAll <img> tags ({len(imgs)}):")
for img in imgs:
    src = img.get("src", "NO_SRC")
    alt = img.get("alt", "")
    iid = img.get("id", "")
    cls = img.get("class", "")
    print(f"  id={iid}, src={src[:100]}, alt={alt}, class={cls}")

# Check for captcha-related elements
print(f"\nCaptcha-related elements:")
captcha_elements = soup.find_all(id=re.compile("captcha", re.IGNORECASE))
for el in captcha_elements:
    print(f"  tag={el.name}, id={el.get('id')}, class={el.get('class')}")
    if el.name == "img":
        print(f"    src={el.get('src', 'NO_SRC')[:200]}")

# Check for canvas elements (sometimes captcha is drawn on canvas)
canvases = soup.find_all("canvas")
print(f"\nCanvas elements: {len(canvases)}")

# Look for any hidden fields that might contain captcha info
hidden_fields = soup.find_all("input", {"type": "hidden"})
print(f"\nHidden fields ({len(hidden_fields)}):")
for hf in hidden_fields:
    name = hf.get("name", "NO_NAME")
    val = hf.get("value", "")[:80]
    print(f"  {name} = {val}")

# Look at all scripts for captcha generation logic
scripts = soup.find_all("script")
print(f"\nScripts mentioning 'captcha' or 'Captcha':")
for s in scripts:
    if s.string and ("captcha" in s.string.lower() or "Captcha" in s.string):
        # Print relevant portions
        lines = s.string.split("\n")
        for line in lines:
            if "captcha" in line.lower():
                print(f"  {line.strip()[:150]}")

# Print all script src URLs
print(f"\nScript sources:")
for s in scripts:
    src = s.get("src", "")
    if src:
        print(f"  {src}")

# Check if there's a captcha handler URL
captcha_img = soup.find("img", {"id": re.compile("captcha", re.IGNORECASE)})
if captcha_img:
    captcha_src = captcha_img.get("src", "")
    print(f"\nCaptcha image src: {captcha_src}")
    
    if captcha_src.startswith("data:"):
        print("  Captcha is a base64 data URI")
        # Extract and save the image
        b64_data = captcha_src.split(",", 1)[1] if "," in captcha_src else ""
        print(f"  Base64 length: {len(b64_data)}")
    else:
        # Try to download the captcha image
        if not captcha_src.startswith("http"):
            captcha_src = BASE_URL + "/" + captcha_src.lstrip("/")
        print(f"  Full URL: {captcha_src}")
        r = session.get(captcha_src)
        print(f"  Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}, Length: {len(r.content)}")

# Also search the full HTML for captcha-related content
print(f"\nSearching full HTML for captcha patterns...")
html = response.text
# Find captcha image pattern
captcha_patterns = re.findall(r'captcha[^"\']*["\']?\s*(?:src|value)\s*=\s*["\']([^"\']*)["\']', html, re.IGNORECASE)
print(f"  Captcha-related src/value attributes: {captcha_patterns}")

# Check if the captcha value is in any cookie
print(f"\nCookies after loading password page:")
for c in session.cookies:
    print(f"  {c.name} = {c.value[:80]} (domain={c.domain})")

# Check for inline JavaScript that sets captcha
for match in re.finditer(r'(captcha[^;]{0,200})', html, re.IGNORECASE):
    print(f"\n  Context: ...{match.group(0)[:150]}...")

# Download and save the full password page HTML for analysis
print(f"\n\nFull password page HTML (captcha area, ~2000 chars around captcha):")
idx = html.lower().find("captcha")
if idx >= 0:
    start = max(0, idx - 500)
    end = min(len(html), idx + 1500)
    print(html[start:end])
