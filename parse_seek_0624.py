#!/usr/bin/env python3
"""Parse SEEK job alert emails - scan 6/24 edition, focused on newest emails."""
import os
import re
import json
from pathlib import Path
from html.parser import HTMLParser

# New email content files from this scan
TOOL_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\a1884051-694f-40a9-93a7-df49b94c66a2\tool-results")

class SeekJobExtractor(HTMLParser):
    """Extract job listings from SEEK email HTML."""
    def __init__(self):
        super().__init__()
        self.jobs = []
        self.in_job_block = False
        self.current_job = {}
        self.tag_stack = []
        self.current_a_href = ""
        self.current_a_text = ""
        self.in_a = False
        self.all_links = []
        self.depth = 0
        self.text_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a':
            href = attrs_dict.get('href', '')
            self.in_a = True
            self.current_a_href = href
            self.current_a_text = ""
        self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_a:
            self.in_a = False
            text = self.current_a_text.strip()
            if text and 'nz.seek.co.nz' in self.current_a_href:
                self.all_links.append({'text': text, 'href': self.current_a_href})
            self.current_a_text = ""
            self.current_a_href = ""
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_a:
            self.current_a_text += data


def parse_email(filepath):
    """Parse SEEK email and extract all job links with context."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Try JSON envelope
    try:
        data = json.loads(raw)
        body = data.get('data', {}).get('data', {}).get('body', '')
        subject = data.get('data', {}).get('data', {}).get('subject', '')
        date = data.get('data', {}).get('data', {}).get('created_at', '')
    except (json.JSONDecodeError, TypeError):
        body = raw
        subject = ''
        date = ''

    # Clean HTML
    body_clean = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body_clean = re.sub(r'<script[^>]*>.*?</script>', '', body_clean, flags=re.DOTALL)

    # Extract links
    parser = SeekJobExtractor()
    parser.feed(body_clean)

    # Also get plain text for context
    plain = re.sub(r'<[^>]+>', ' ', body_clean)
    plain = re.sub(r'\s+', ' ', plain)

    # NZ locations
    nz_locs = [
        'Auckland CBD', 'Wellington Central', 'Christchurch Central',
        'Hamilton Central', 'Tauranga Central', 'Invercargill Central',
        'New Plymouth Central', 'Ponsonby', 'Henderson', 'Mount Wellington',
        'Parnell', 'Takapuna', 'Onehunga', 'East Tamaki', 'Manukau',
        'Matangi', 'Auckland', 'Wellington', 'Christchurch', 'Hamilton',
        'Tauranga', 'Invercargill', 'New Plymouth', 'Napier', 'Dunedin',
        'Southland', 'Canterbury', 'Waikato', 'Bay of Plenty', 'Taranaki',
        'Otago', 'Northland', 'Hawke\'s Bay', 'Gisborne', 'Marlborough',
        'Nelson', 'West Coast', 'Manawatu', 'Whanganui', 'Wairarapa',
        'Rotorua', 'Whangarei', 'Palmerston North', 'Lower Hutt',
        'Porirua', 'Upper Hutt', 'Rangiora', 'Ashburton', 'Timaru',
        'Oamaru', 'Queenstown', 'Wanaka', 'Alexandra'
    ]

    jobs = []
    skip_words = ['view all', 'unsubscribe', 'update', 'delete', 'manage',
                  'privacy', 'contact', 'seek profile', 'start my search',
                  'save this search', 'recommended', 'saved search', 'see more',
                  'apply now', 'learn more']

    for link in parser.all_links:
        text = link['text']
        href = link['href']

        # Skip non-job links
        if any(w in text.lower() for w in skip_words):
            continue

        # Only process links that look like job titles (not navigation/footer)
        if '/job/' in href or (text and len(text) > 5 and text[0].isupper()):
            # Find context in plain text
            idx = plain.find(text)
            if idx >= 0:
                after = plain[idx + len(text):idx + 500].strip()
            else:
                after = ''

            # Extract salary
            sal_match = re.search(
                r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year|annum))?',
                after)
            salary = sal_match.group() if sal_match else ''

            # Also check for competitive/other salary descriptions
            if not salary:
                sal_desc = re.search(
                    r'(Competitive[^,.]*|Base\s[^,.]*|[^\s]+\s+per\s+(?:hour|year))',
                    after[:200])
                if sal_desc:
                    salary = sal_desc.group()

            # Extract location
            location = ''
            for loc in sorted(nz_locs, key=lambda x: -len(x)):  # longer names first
                if loc in after[:400]:
                    location = loc
                    break

            # Extract company (between title and location)
            company = ''
            if location:
                loc_idx = after.find(location)
                between = after[:loc_idx].strip()
                if between and len(between) < 120:
                    company = between

            # Determine if this is a real job listing
            if '/job/' in href or (location and salary) or (location and company):
                jobs.append({
                    'title': text,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'link': href,
                    'email_date': date,
                    'email_subject': subject
                })

    return jobs, subject, date


def deduplicate(all_jobs):
    seen = set()
    unique = []
    for j in all_jobs:
        key = f"{j['title']}|{j['company']}|{j['location']}"
        if key not in seen:
            seen.add(key)
            unique.append(j)
    return unique


# Process the 3 newest email files
files = sorted(TOOL_DIR.glob("mcp-connector-proxy-qq-mail_GetMessage*.txt"))
all_jobs = []

for f in files:
    jobs, subject, date = parse_email(f)
    print(f"File: {f.name}")
    print(f"  Subject: {subject[:80]}")
    print(f"  Date: {date}")
    print(f"  Jobs found: {len(jobs)}")
    for j in jobs[:10]:
        print(f"    - {j['title']} | {j.get('company','')} | {j.get('location','')} | {j.get('salary','')}")
    if len(jobs) > 10:
        print(f"    ... and {len(jobs)-10} more")
    all_jobs.extend(jobs)

print(f"\nTotal jobs from email files: {len(all_jobs)}")

# Deduplicate
unique = deduplicate(all_jobs)
print(f"Unique jobs: {len(unique)}")

# Also collect jobs from SearchMessages snippets (comprehensive)
snippet_jobs = []

# 6/23 ICT 21:47 (msg_nfhPt2rEa2o8tKMef8muDi-iQ3kDfn5YNC-2NHEE0yhWBg)
snippet_jobs.extend([
    {"title": "Business Analyst (6M Contract)", "company": "Sourced | IT Recruitment Specialists", "location": "Auckland CBD, Auckland", "salary": "", "link": "", "email_date": "2026-06-23T21:47:15Z"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-23T21:47:15Z"},
    {"title": "Business Operations Analyst", "company": "Cultivate", "location": "Auckland CBD, Auckland", "salary": "Base + Bonus + insurances + more", "link": "", "email_date": "2026-06-23T21:47:15Z"},
])

# 6/23 ICT 20:25 (msg_xqgheVShpNHcLLImKciPAv9plZG-MhNaO6-GE6msBPB2Zw)
snippet_jobs.extend([
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-23T20:25:31Z"},
    {"title": "Business Operations Analyst", "company": "Cultivate", "location": "Auckland CBD, Auckland", "salary": "Base + Bonus + insurances + more", "link": "", "email_date": "2026-06-23T20:25:31Z"},
    {"title": "Business Analyst (6M Contract)", "company": "Sourced | IT Recruitment Specialists", "location": "Auckland CBD, Auckland", "salary": "", "link": "", "email_date": "2026-06-23T20:25:31Z"},
])

# 6/23 Admin 23:58 (msg_PD0yypczdGwU6pZe26GmdEa0bxQJoqaxVYeZF2qz_s2_Tw)
snippet_jobs.extend([
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Henderson, Auckland", "salary": "$51,000 per year", "link": "", "email_date": "2026-06-23T23:58:17Z"},
    {"title": "IT Support Engineer", "company": "Morgan Furniture Int Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-23T23:58:17Z"},
    {"title": "Operations & Administration Manager", "company": "The Life Centre", "location": "Ponsonby, Auckland", "salary": "$75,000 – $80,000 per year", "link": "", "email_date": "2026-06-23T23:58:17Z"},
    {"title": "Office Co-Ordinator", "company": "Flo & Frankie", "location": "Parnell, Auckland", "salary": "Competitive pay and great perks", "link": "", "email_date": "2026-06-23T23:58:17Z"},
])

# 6/22 emails
snippet_jobs.extend([
    {"title": "Project Business Analyst", "company": "PowerNet", "location": "Invercargill Central, Southland", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Wellington Central, Wellington", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Senior Business Analyst", "company": "Absol", "location": "", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Henderson, Auckland", "salary": "$51,000 per year", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    {"title": "Office Co-Ordinator", "company": "Flo & Frankie", "location": "Parnell, Auckland", "salary": "Competitive pay and great perks", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    {"title": "Office Manager", "company": "Fraundorfer Ltd", "location": "Tauranga Central, Bay of Plenty", "salary": "", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    {"title": "Finance & People Administrator (part-time)", "company": "Pie Funds Management Limited", "location": "Takapuna, Auckland", "salary": "", "link": "", "email_date": "2026-06-22T23:58:14Z"},
])

# 6/21 emails
snippet_jobs.extend([
    {"title": "Office Administrator / Manager", "company": "Simtec Therapeutic Limited", "location": "Onehunga, Auckland", "salary": "$65,000 – $85,000 per year", "link": "", "email_date": "2026-06-21T23:58:15Z"},
    {"title": "Office Manager", "company": "Finelawn Limited", "location": "Matangi, Waikato", "salary": "$75,000 – $90,000 per year + Bonus", "link": "", "email_date": "2026-06-21T23:58:15Z"},
    {"title": "Information Systems & Technology Support Analyst", "company": "Craigmore Corporate", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-21T23:58:15Z"},
    {"title": "Business Analyst", "company": "New Plymouth District Council", "location": "New Plymouth Central, Taranaki", "salary": "", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    {"title": "Graduate Functional Consultant", "company": "Credisense Limited", "location": "Auckland CBD, Auckland", "salary": "", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    {"title": "Data Analyst", "company": "Frog Recruitment - Auckland", "location": "Auckland CBD, Auckland", "salary": "$40 per hour", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    {"title": "Senior Technical Business Analyst", "company": "New Zealand Customs Service", "location": "Wellington Central, Wellington", "salary": "Competitive salary - in-house gym facility", "link": "", "email_date": "2026-06-21T21:47:15Z"},
])

# 6/20 & 6/19 emails (already covered in previous scan, but include for completeness)
snippet_jobs.extend([
    {"title": "Business Systems Analyst - ERP", "company": "Windsor Engineering Group Ltd", "location": "Mount Wellington, Auckland", "salary": "Competitive annual salary + employee benefits", "link": "", "email_date": "2026-06-19T22:47:15Z"},
    {"title": "System Analyst", "company": "Morgan Furniture Int Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-19T22:47:15Z"},
    {"title": "IT Support & AI Business Analyst", "company": "Miles Construction Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-18T21:47:16Z"},
    {"title": "Technical BA", "company": "Techspace Consulting Limited", "location": "", "salary": "$40 per hour", "link": "", "email_date": "2026-06-18T21:47:16Z"},
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Mount Wellington, Auckland", "salary": "$51,000 per year", "link": "", "email_date": "2026-06-18T23:58:15Z"},
    {"title": "Customer Service Administrator", "company": "Auckland RV Centre", "location": "East Tamaki, Auckland", "salary": "$25 – $30 per hour", "link": "", "email_date": "2026-06-18T23:58:15Z"},
    {"title": "Junior IT Sales and Support Technician", "company": "Computer Aid", "location": "Cambridge, Waikato", "salary": "", "link": "", "email_date": "2026-06-18T23:58:15Z"},
])

# Combine all sources
all_jobs.extend(snippet_jobs)
unique = deduplicate(all_jobs)

# Sort by relevance
def sort_key(j):
    t = j.get('title', '').lower()
    if 'mechanical' in t: return 0
    if 'erp' in t: return 1
    if 'business system' in t: return 2
    if 'business analyst' in t and 'senior' in t or 'technical' in t: return 3
    if 'business analyst' in t: return 4
    if 'data analyst' in t: return 5
    if 'it support' in t or 'information system' in t: return 6
    if 'system analyst' in t: return 7
    if 'functional consultant' in t: return 8
    if 'operations' in t and 'admin' in t: return 9
    if 'office' in t or 'admin' in t: return 10
    return 11

unique.sort(key=sort_key)

# Save raw data
output_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw_0624.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"\n=== FINAL DEDUPLICATED JOB LIST ===")
print(f"Total unique jobs: {len(unique)}")
for j in unique:
    print(f"  [{j.get('email_date','')[:10]}] {j['title']} | {j.get('company','')} | {j.get('location','')} | {j.get('salary','')}")

print(f"\nSaved to: {output_path}")
