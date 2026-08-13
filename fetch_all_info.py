"""
CUIMS Data Fetcher v2 - Fetch ALL information including previous session marks
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import io
import os
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

UID = "24BCS10029"
PASSWORD = "Skill1000@"
BASE_URL = "https://students.cuchd.in"
HEADERS_JSON = {"Content-Type": "application/json"}

def sep(title):
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")

def login():
    sess = requests.Session()
    r = sess.get(BASE_URL + "/")
    soup = BeautifulSoup(r.text, "html.parser")
    vs = soup.find("input", {"name": "__VIEWSTATE"})
    vsg = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    data = {"txtUserId": UID, "btnNext": "NEXT"}
    if vs: data["__VIEWSTATE"] = vs["value"]
    if vsg: data["__VIEWSTATEGENERATOR"] = vsg["value"]
    
    r = sess.post(BASE_URL + "/", data=data, allow_redirects=False)
    pwd_url = BASE_URL + r.headers.get("Location", "")
    r = sess.get(pwd_url)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Download captcha
    captcha_img = soup.find("img", {"id": "imgCaptcha"})
    captcha_src = captcha_img.get("src", "")
    if not captcha_src.startswith("http"):
        captcha_src = BASE_URL + "/" + captcha_src.lstrip("/")
    cr = sess.get(captcha_src)
    cpath = os.path.join(os.path.dirname(__file__), "captcha.jpg")
    with open(cpath, "wb") as f: f.write(cr.content)
    print(f"Captcha saved to: {cpath}")
    captcha_val = input("Enter captcha: ").strip()
    
    vs = soup.find("input", {"name": "__VIEWSTATE"})
    ev = soup.find("input", {"name": "__EVENTVALIDATION"})
    vsg = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    
    pwd_data = {"txtLoginPassword": PASSWORD, "txtcaptcha": captcha_val, "btnLogin": "LOGIN"}
    if vs: pwd_data["__VIEWSTATE"] = vs["value"]
    if ev: pwd_data["__EVENTVALIDATION"] = ev["value"]
    if vsg: pwd_data["__VIEWSTATEGENERATOR"] = vsg["value"]
    
    r = sess.post(pwd_url, data=pwd_data, allow_redirects=False)
    if r.status_code in (301, 302):
        dash = r.headers.get("Location", "")
        if dash.startswith("/"): dash = BASE_URL + dash
        sess.get(dash)
        print("[OK] Login successful!")
        return sess
    else:
        print(f"[FAIL] Login failed: {r.status_code}")
        return None

def main():
    sep("CUIMS DATA FETCHER v2")
    print(f"Student ID: {UID}")
    
    sess = login()
    if not sess:
        sys.exit(1)
    
    # === FULL NAME ===
    sep("STUDENT PROFILE")
    r = sess.get(BASE_URL + "/frmAccountStudentDetails.aspx")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        user_div = soup.find("div", {"class": "user-n-mob"})
        if user_div:
            print(f"Full Name: {user_div.get_text(strip=True)}")
    
    # === ATTENDANCE ===
    sep("ATTENDANCE (Current Session)")
    att_url = BASE_URL + "/frmStudentCourseWiseAttendanceSummary.aspx?type=etgkYfqBdH1fSfc255iYGw=="
    r = sess.get(att_url)
    
    attendance_data = None
    report_id = None
    session_id = None
    
    if r.status_code == 200 and "getReport" in r.text:
        # Extract session & report IDs
        sb = r.text.find("CurrentSession")
        so = sb + r.text[sb:].find("(")
        se = sb + r.text[sb:].find(")")
        session_id = r.text[so+1:se]
        
        jb = r.text.find("getReport")
        iq = jb + r.text[jb:].find("'")
        eq = iq + r.text[iq+1:].find("'")
        report_id = r.text[iq+1:eq+1]
        
        rpt_url = BASE_URL + "/frmStudentCourseWiseAttendanceSummary.aspx/GetReport"
        jdata = "{UID:'" + report_id + "',Session:'" + session_id + "'}"
        r2 = sess.post(rpt_url, headers=HEADERS_JSON, data=jdata)
        
        if r2.status_code == 200:
            attendance_data = json.loads(json.loads(r2.text)["d"])
            
            print(f"\n{'#':<4} {'Subject':<50} {'Delivered':>10} {'Attended':>10} {'Duty':>7} {'Medical':>9} {'%':>7}")
            print("-" * 100)
            for i, s in enumerate(attendance_data, 1):
                title = s.get("Title", "N/A")
                delivered = s.get("Lec_Delivered", 0)
                attended = s.get("Lec_Attended", 0)
                duty = s.get("DutyLeave_Lec", 0)
                medical = s.get("MedicalLeave_Lec", 0) 
                pct = s.get("TotalPercentage", "N/A")
                print(f"{i:<4} {title:<50} {str(delivered):>10} {str(attended):>10} {str(duty):>7} {str(medical):>9} {str(pct):>6}%")
            
            # Full attendance
            sep("DAY-WISE ATTENDANCE DETAILS")
            full_rpt_url = BASE_URL + "/frmStudentCourseWiseAttendanceSummary.aspx/GetFullReport"
            for s in attendance_data:
                title = s.get("Title", "N/A")
                ec = s.get("EncryptCode", "")
                fd = "{course:'" + ec + "',UID:'" + report_id + "',fromDate:'',toDate:'',type:'All',Session:'" + session_id + "'}"
                r3 = sess.post(full_rpt_url, headers=HEADERS_JSON, data=fd)
                if r3.status_code == 200:
                    try:
                        d_val = json.loads(r3.text)["d"]
                        if isinstance(d_val, str):
                            full_data = json.loads(d_val)
                            if full_data:
                                print(f"\n  {title}:")
                                print(f"  {'Date':<25} {'Status':<15} {'Marked By':<20}")
                                print(f"  {'-'*60}")
                                for entry in full_data:
                                    date = entry.get("Date", "?")
                                    status = entry.get("Status", "?")
                                    by = entry.get("MarkedBy", "?")
                                    print(f"  {str(date):<25} {str(status):<15} {str(by):<20}")
                            else:
                                print(f"\n  {title}: No day-wise data yet")
                        elif isinstance(d_val, dict):
                            result = d_val.get("Result", "")
                            if result == "No Data Found":
                                print(f"\n  {title}: No day-wise data (new session)")
                            else:
                                print(f"\n  {title}: {result}")
                    except:
                        print(f"\n  {title}: No day-wise data available")
    
    # === MARKS ===
    sep("MARKS (All Sessions)")
    marks_url = BASE_URL + "/frmStudentMarksView.aspx"
    r = sess.get(marks_url)
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        select_tag = soup.find("select", {"name": re.compile("ddlCAndPSession", re.IGNORECASE)})
        
        if select_tag:
            options = select_tag.find_all("option")
            print(f"\nAvailable Sessions:")
            for opt in options:
                marker = " <-- CURRENT" if opt.get("selected") else ""
                print(f"  {opt.get_text(strip=True)}{marker} (value: {opt['value']})")
            
            # Fetch marks for EACH session
            for opt in options:
                sess_val = opt["value"]
                sess_name = opt.get_text(strip=True)
                
                sep(f"MARKS - {sess_name}")
                
                # Re-fetch the page to get fresh viewstate
                r = sess.get(marks_url)
                soup = BeautifulSoup(r.text, "html.parser")
                vs = soup.find("input", {"name": "__VIEWSTATE"})
                ev = soup.find("input", {"name": "__EVENTVALIDATION"})
                
                md = {}
                if vs: md["__VIEWSTATE"] = vs["value"]
                if ev: md["__EVENTVALIDATION"] = ev["value"]
                md["ctl00$ContentPlaceHolder1$wucStudentMarksView$ddlCAndPSession"] = sess_val
                
                r2 = sess.post(marks_url, data=md)
                soup2 = BeautifulSoup(r2.text, "html.parser")
                accordion = soup2.find("div", {"id": "accordion"})
                
                if accordion:
                    subject_names = [i.get_text().strip() for i in accordion.find_all("h3")]
                    divs = accordion.find_all("div")
                    
                    for i in range(min(len(subject_names), len(divs))):
                        print(f"\n  >> {subject_names[i]}")
                        tbody = divs[i].find("tbody")
                        if tbody:
                            trs = tbody.find_all("tr")
                            print(f"     {'Component':<45} {'Total':>8} {'Obtained':>10}")
                            print(f"     {'-'*65}")
                            for tr in trs:
                                tds = tr.find_all("td")
                                if len(tds) >= 3:
                                    el = tds[0].get_text(strip=True)
                                    tot = tds[1].get_text(strip=True)
                                    obt = tds[2].get_text(strip=True)
                                    print(f"     {el:<45} {tot:>8} {obt:>10}")
                else:
                    print("  No marks data available for this session")
    
    # === TIMETABLE ===
    sep("TIMETABLE")
    tt_url = BASE_URL + "/frmMyTimeTable.aspx"
    r = sess.get(tt_url)
    
    if r.status_code == 200 and len(r.text) > 500:
        soup = BeautifulSoup(r.text, "html.parser")
        vs = soup.find("input", {"name": "__VIEWSTATE"})
        
        if vs:
            td = {
                "__VIEWSTATE": vs["value"],
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ReportViewer1$ctl09$Reserved_AsyncLoadTarget",
            }
            r2 = sess.post(tt_url, data=td)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            
            mapping_table = soup2.find("table", {"id": "ContentPlaceHolder1_gvMyTimeTableDetails"})
            if mapping_table:
                print("\nCourse Codes:")
                for row in mapping_table.find_all("tr"):
                    tds = row.find_all("td")
                    if len(tds) > 1:
                        print(f"  {tds[0].get_text(strip=True)} -> {tds[1].get_text(strip=True)}")
            
            tt_table = soup2.find("table", {"id": "ContentPlaceHolder1_gvMyTimeTable"})
            if tt_table:
                print("\nWeekly Schedule:")
                rows = tt_table.find_all("tr")
                if rows:
                    ths = rows[0].find_all("th")
                    header = [th.get_text(strip=True) for th in ths]
                    col_widths = [max(12, len(h)+2) for h in header]
                    
                    header_line = " | ".join(h.ljust(w) for h, w in zip(header, col_widths))
                    print(f"  {header_line}")
                    print(f"  {'-' * len(header_line)}")
                    
                    for row in rows[1:]:
                        tds = row.find_all("td")
                        vals = [td.get_text(strip=True) or "--" for td in tds]
                        row_line = " | ".join(v[:w].ljust(w) for v, w in zip(vals, col_widths))
                        print(f"  {row_line}")
            else:
                print("  Timetable table not found (may not be available for this session)")
    
    sep("ALL DONE! All available CUIMS information has been fetched.")

if __name__ == "__main__":
    main()
