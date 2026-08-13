"""
Full login flow tracer for students.cuchd.in (fixed cookies)
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

UID = "24BCS10029"
PASSWORD = "Skill1000@"

BASE_URL = "https://students.cuchd.in"
LOGIN_URL = BASE_URL + "/"

def print_cookies(sess):
    for c in sess.cookies:
        print(f"  {c.name} = {c.value[:80]} (domain={c.domain}, path={c.path})")

print("=" * 80)
print("  STEP 1: GET login page")
print("=" * 80)

session = requests.Session()
response = session.get(LOGIN_URL)
print(f"Status: {response.status_code}")
print("Cookies:"); print_cookies(session)

soup = BeautifulSoup(response.text, "html.parser")
viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
viewstate_gen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})

data = {}
if viewstate_tag: data["__VIEWSTATE"] = viewstate_tag["value"]
if viewstate_gen: data["__VIEWSTATEGENERATOR"] = viewstate_gen["value"]
data["txtUserId"] = UID
data["btnNext"] = "NEXT"

print(f"\n{'=' * 80}")
print(f"  STEP 2: POST UID")
print(f"{'=' * 80}")

response = session.post(LOGIN_URL, data=data, allow_redirects=False)
print(f"Status: {response.status_code}")
location = response.headers.get("Location", "NONE")
print(f"Location: {location}")
print("Cookies:"); print_cookies(session)

if response.status_code in (301, 302, 303, 307, 308):
    password_url = location
    if password_url.startswith("/"):
        password_url = BASE_URL + password_url
    
    print(f"\n{'=' * 80}")
    print(f"  STEP 3: GET password page")
    print(f"{'=' * 80}")
    
    response = session.get(password_url)
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    print("Cookies:"); print_cookies(session)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    all_inputs = soup.find_all("input")
    print(f"\nAll inputs ({len(all_inputs)}):")
    for inp in all_inputs:
        name = inp.get("name", "NO_NAME")
        itype = inp.get("type", "")
        iid = inp.get("id", "")
        val = inp.get("value", "")[:30]
        print(f"  name={name}, type={itype}, id={iid}, val={val}")
    
    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
    event_validation = soup.find("input", {"name": "__EVENTVALIDATION"})
    viewstate_gen2 = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    
    pwd_data = {}
    if viewstate_tag: pwd_data["__VIEWSTATE"] = viewstate_tag["value"]
    if event_validation: pwd_data["__EVENTVALIDATION"] = event_validation["value"]
    if viewstate_gen2: pwd_data["__VIEWSTATEGENERATOR"] = viewstate_gen2["value"]
    
    pwd_field = soup.find("input", {"type": "password"})
    pwd_field_name = pwd_field.get("name", "txtLoginPassword") if pwd_field else "txtLoginPassword"
    pwd_data[pwd_field_name] = PASSWORD
    print(f"\nPassword field: {pwd_field_name}")
    
    login_btn = soup.find("input", {"type": "submit"})
    if login_btn:
        btn_name = login_btn.get("name", "btnLogin")
        btn_value = login_btn.get("value", "LOGIN")
        pwd_data[btn_name] = btn_value
        print(f"Login button: {btn_name}={btn_value}")
    else:
        pwd_data["btnLogin"] = "LOGIN"
    
    print(f"\n{'=' * 80}")
    print(f"  STEP 4: POST password")
    print(f"{'=' * 80}")
    
    response = session.post(password_url, data=pwd_data, allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Location: {response.headers.get('Location', 'NONE')}")
    print("Cookies:"); print_cookies(session)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        print(f"Title: {title.get_text() if title else 'NO TITLE'}")
        # Check for errors
        body_text = soup.get_text(separator=" ", strip=True)[:500]
        print(f"Body text (first 500): {body_text}")
    
    if response.status_code in (301, 302, 303, 307, 308):
        dashboard_loc = response.headers.get("Location", "")
        if dashboard_loc.startswith("/"):
            dashboard_loc = BASE_URL + dashboard_loc
        elif not dashboard_loc.startswith("http"):
            dashboard_loc = BASE_URL + "/" + dashboard_loc
        
        print(f"\nDashboard URL: {dashboard_loc}")
        
        print(f"\n{'=' * 80}")
        print(f"  STEP 5: GET dashboard")
        print(f"{'=' * 80}")
        
        response = session.get(dashboard_loc, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        print("Cookies:"); print_cookies(session)
        
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        print(f"Title: {title.get_text() if title else 'NO TITLE'}")
        
        # Look for student name
        for selector in ["user-n-mob", "user-name", "student-name", "profile-name"]:
            el = soup.find(class_=re.compile(selector, re.IGNORECASE))
            if el:
                print(f"Found .{selector}: {el.get_text(strip=True)[:100]}")
        
        # Links
        links = soup.find_all("a", href=True)
        print(f"\nNavigable links ({len(links)}):")
        for a in links[:40]:
            href = a.get("href", "")
            text = a.get_text(strip=True)[:60]
            if text or "frm" in href.lower():
                print(f"  {href} -> {text}")
        
        # ---- Try fetching attendance ----
        print(f"\n{'=' * 80}")
        print(f"  STEP 6: Fetch attendance")
        print(f"{'=' * 80}")
        
        att_url = BASE_URL + "/frmStudentCourseWiseAttendanceSummary.aspx?type=etgkYfqBdH1fSfc255iYGw=="
        r = session.get(att_url, allow_redirects=True)
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        
        if r.status_code == 200 and len(r.text) > 500:
            s = BeautifulSoup(r.text, "html.parser")
            t = s.find("title")
            print(f"Title: {t.get_text() if t else 'NO TITLE'}")
            
            has_report = "getReport" in r.text
            has_session = "CurrentSession" in r.text
            print(f"Has getReport: {has_report}")
            print(f"Has CurrentSession: {has_session}")
            
            if has_session:
                session_block = r.text.find("CurrentSession")
                session_block_origin = session_block + r.text[session_block:].find("(")
                session_block_end = session_block + r.text[session_block:].find(")")
                current_session_id = r.text[session_block_origin + 1 : session_block_end]
                print(f"Current Session ID: {current_session_id}")
            
            if has_report:
                js_report_block = r.text.find("getReport")
                initial_q = js_report_block + r.text[js_report_block:].find("'")
                ending_q = initial_q + r.text[initial_q + 1:].find("'")
                report_id = r.text[initial_q + 1 : ending_q + 1]
                print(f"Report ID: {report_id}")
                
                # Fetch JSON attendance
                report_url = BASE_URL + "/frmStudentCourseWiseAttendanceSummary.aspx/GetReport"
                json_data = "{UID:'" + report_id + "',Session:'" + current_session_id + "'}"
                headers = {"Content-Type": "application/json"}
                
                r2 = session.post(report_url, headers=headers, data=json_data)
                print(f"\nGetReport Status: {r2.status_code}")
                
                if r2.status_code == 200:
                    try:
                        attendance = json.loads(r2.text)["d"]
                        attendance_data = json.loads(attendance)
                        
                        print(f"\n{'=' * 80}")
                        print(f"  ATTENDANCE DATA")
                        print(f"{'=' * 80}")
                        print(f"\n{'Subject':<55} {'Attended':>10} {'Total':>8} {'%':>8}")
                        print("-" * 85)
                        for subj in attendance_data:
                            title = subj.get("Title", "N/A")
                            pct = subj.get("TotalPercentage", "N/A")
                            present = subj.get("Lec_Attended", "?")
                            total = subj.get("Lec_Delivered", "?")
                            print(f"{title:<55} {str(present):>10} {str(total):>8} {str(pct):>7}%")
                        
                        # Full attendance for each subject
                        print(f"\n{'=' * 80}")
                        print(f"  FULL ATTENDANCE (Day-wise)")
                        print(f"{'=' * 80}")
                        full_report_url = BASE_URL + "/frmStudentCourseWiseAttendanceSummary.aspx/GetFullReport"
                        for subj in attendance_data:
                            title = subj.get("Title", "N/A")
                            encrypt_code = subj.get("EncryptCode", "")
                            print(f"\n--- {title} ---")
                            
                            fdata = (
                                "{course:'" + encrypt_code + 
                                "',UID:'" + report_id + 
                                "',fromDate: '',toDate:''" +
                                ",type:'All'" +
                                ",Session:'" + current_session_id + "'}"
                            )
                            r3 = session.post(full_report_url, headers=headers, data=fdata)
                            if r3.status_code == 200:
                                try:
                                    full_data = json.loads(json.loads(r3.text)["d"])
                                    for entry in full_data[:10]:
                                        date = entry.get("Date", "?")
                                        status = entry.get("Status", "?")
                                        print(f"  {date}  ->  {status}")
                                    if len(full_data) > 10:
                                        print(f"  ... and {len(full_data) - 10} more entries")
                                except:
                                    print(f"  Could not parse full attendance: {r3.text[:200]}")
                            else:
                                print(f"  Failed: {r3.status_code}")
                        
                    except Exception as e:
                        print(f"Error parsing attendance: {e}")
                        print(f"Raw response: {r2.text[:500]}")
        
        # ---- Try fetching timetable ----
        print(f"\n{'=' * 80}")
        print(f"  TIMETABLE")
        print(f"{'=' * 80}")
        
        tt_url = BASE_URL + "/frmMyTimeTable.aspx"
        r = session.get(tt_url, allow_redirects=True)
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        
        if r.status_code == 200 and len(r.text) > 500:
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.find("title")
            print(f"Title: {title_tag.get_text() if title_tag else 'NO TITLE'}")
            
            viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
            if viewstate_tag:
                tt_data = {
                    "__VIEWSTATE": viewstate_tag["value"],
                    "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ReportViewer1$ctl09$Reserved_AsyncLoadTarget",
                }
                r2 = session.post(tt_url, data=tt_data)
                soup2 = BeautifulSoup(r2.text, "html.parser")
                
                tt_table = soup2.find("table", {"id": "ContentPlaceHolder1_gvMyTimeTable"})
                mapping_table = soup2.find("table", {"id": "ContentPlaceHolder1_gvMyTimeTableDetails"})
                
                if tt_table:
                    print("\nTimetable found!")
                    rows = tt_table.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_text = " | ".join(c.get_text(strip=True)[:20] for c in cells)
                        print(f"  {row_text}")
                else:
                    print("  Timetable table not found in response")
                    # Print what tables exist
                    tables = soup2.find_all("table")
                    print(f"  Found {len(tables)} tables")
                    for t in tables[:5]:
                        print(f"    id={t.get('id')}, class={t.get('class')}")
                
                if mapping_table:
                    print("\nCourse Code Mapping:")
                    rows = mapping_table.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_text = " | ".join(c.get_text(strip=True)[:40] for c in cells)
                        print(f"  {row_text}")
        
        # ---- Try fetching marks ----
        print(f"\n{'=' * 80}")
        print(f"  MARKS")
        print(f"{'=' * 80}")
        
        marks_url = BASE_URL + "/frmStudentMarksView.aspx"
        r = session.get(marks_url, allow_redirects=True)
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        
        if r.status_code == 200 and len(r.text) > 500:
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.find("title")
            print(f"Title: {title_tag.get_text() if title_tag else 'NO TITLE'}")
            
            # Find session dropdown
            select_tag = soup.find("select", {"name": re.compile("ddlCAndPSession", re.IGNORECASE)})
            if select_tag:
                options = select_tag.findAll("option")
                print(f"\nAvailable Sessions ({len(options)}):")
                current_session_marks = None
                for opt in options:
                    is_selected = opt.get("selected") is not None
                    marker = " <-- CURRENT" if is_selected else ""
                    print(f"  {opt['value']} - {opt.get_text(strip=True)}{marker}")
                    if is_selected:
                        current_session_marks = opt["value"]
                
                if current_session_marks:
                    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
                    event_validation = soup.find("input", {"name": "__EVENTVALIDATION"})
                    marks_data = {}
                    if viewstate_tag: marks_data["__VIEWSTATE"] = viewstate_tag["value"]
                    if event_validation: marks_data["__EVENTVALIDATION"] = event_validation["value"]
                    marks_data["ctl00$ContentPlaceHolder1$wucStudentMarksView$ddlCAndPSession"] = current_session_marks
                    
                    r2 = session.post(marks_url, data=marks_data)
                    soup2 = BeautifulSoup(r2.text, "html.parser")
                    accordion = soup2.find("div", {"id": "accordion"})
                    
                    if accordion:
                        subject_names = [i.get_text().strip() for i in accordion.findAll("h3")]
                        divs = accordion.findAll("div")
                        
                        for i in range(min(len(subject_names), len(divs))):
                            print(f"\n  Subject: {subject_names[i]}")
                            tbody = divs[i].find("tbody")
                            if tbody:
                                trs = tbody.findAll("tr")
                                for tr in trs:
                                    tds = tr.findAll("td")
                                    if len(tds) >= 3:
                                        element = tds[0].get_text(strip=True)
                                        total = tds[1].get_text(strip=True)
                                        obtained = tds[2].get_text(strip=True)
                                        print(f"    {element:<40} {total:>8} {obtained:>10}")
                    else:
                        print("  No accordion/marks data found")
            else:
                print("  Session dropdown not found")
        
        # ---- Profile / Full Name ----
        print(f"\n{'=' * 80}")
        print(f"  PROFILE / FULL NAME")
        print(f"{'=' * 80}")
        
        profile_urls = [
            BASE_URL + "/frmAccountStudentDetails.aspx",
            BASE_URL + "/frmStudentProfile.aspx",
        ]
        for purl in profile_urls:
            r = session.get(purl, allow_redirects=True)
            print(f"\n{purl}")
            print(f"  Status: {r.status_code}, Len: {len(r.text)}")
            if r.status_code == 200 and len(r.text) > 500:
                soup = BeautifulSoup(r.text, "html.parser")
                user_div = soup.find("div", {"class": "user-n-mob"})
                if user_div:
                    print(f"  Full Name: {user_div.get_text(strip=True)}")
                # Try other common name selectors
                for cls_name in ["userName", "student_name", "fullName", "user-n-mob"]:
                    el = soup.find(class_=re.compile(cls_name, re.IGNORECASE))
                    if el:
                        print(f"  .{cls_name}: {el.get_text(strip=True)[:100]}")

print(f"\n{'=' * 80}")
print(f"  ALL DONE!")
print(f"{'=' * 80}")
