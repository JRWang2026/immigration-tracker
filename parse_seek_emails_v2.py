#!/usr/bin/env python3
"""Parse SEEK job alert emails with BeautifulSoup for structured extraction."""
import os
import re
import json
from pathlib import Path

# Use built-in HTML parser since bs4 may not be installed
from html.parser import HTMLParser

TOOL_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\1c20b8bf-2fd1-42a9-b2d6-95331b066b4d\tool-results")

class SeekEmailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.jobs = []
        self.current_text = ""
        self.current_href = ""
        self.in_a_tag = False
        self.all_links = []
        self.all_text = []
        self.text_stack = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a':
            href = attrs_dict.get('href', '')
            self.in_a_tag = True
            self.current_href = href
            self.current_text = ""
        self.text_stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_a_tag:
            self.in_a_tag = False
            text = self.current_text.strip()
            if text:
                self.all_links.append({
                    'text': text,
                    'href': self.current_href
                })
            self.current_text = ""
            self.current_href = ""
        if self.text_stack and self.text_stack[-1] == tag:
            self.text_stack.pop()

    def handle_data(self, data):
        if self.in_a_tag:
            self.current_text += data


def parse_email_file(filepath):
    """Parse a SEEK email file and extract job listings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Parse JSON envelope
    try:
        data = json.loads(raw)
        body = data.get('data', {}).get('data', {}).get('body', '')
        subject = data.get('data', {}).get('data', {}).get('subject', '')
        date = data.get('data', {}).get('data', {}).get('created_at', '')
    except json.JSONDecodeError:
        body = raw
        subject = ''
        date = ''

    # Clean HTML - remove style/script tags
    body_clean = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    body_clean = re.sub(r'<script[^>]*>.*?</script>', '', body_clean, flags=re.DOTALL)

    # Extract all links with text
    parser = SeekEmailParser()
    parser.feed(body_clean)

    # Also extract plain text version
    plain_text = re.sub(r'<[^>]+>', ' ', body_clean)
    plain_text = re.sub(r'\s+', ' ', plain_text)

    # Now extract job listings from links
    # SEEK job links contain job titles as link text, company/location/salary nearby
    jobs = []

    # Find all links pointing to nz.seek.co.nz
    seek_links = [l for l in parser.all_links if 'nz.seek.co.nz' in l.get('href', '')]

    for link in seek_links:
        link_text = link['text']
        link_href = link['href']

        # Skip non-job links (view all, unsubscribe, etc.)
        if any(skip in link_text.lower() for skip in ['view all', 'unsubscribe', 'update', 'delete', 'manage', 'privacy', 'contact', 'seek profile', 'start my search']):
            continue

        # Find context around this link text in the plain text
        idx = plain_text.find(link_text)
        if idx >= 0:
            # Get surrounding context (before and after)
            before = plain_text[max(0, idx-200):idx].strip()
            after = plain_text[idx+len(link_text):idx+400].strip()
        else:
            before = ''
            after = ''

        # Determine what type of link this is
        if '/job/' in link_href:
            # This is a direct job link
            job_title = link_text
            # Extract salary from after text
            sal_match = re.search(r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year|annum))?', after)
            salary = sal_match.group() if sal_match else ''

            # Extract location from after text
            nz_locs = ['Auckland CBD', 'Wellington Central', 'Christchurch Central',
                       'Hamilton Central', 'Tauranga Central', 'Invercargill Central',
                       'New Plymouth Central', 'Auckland', 'Wellington', 'Christchurch',
                       'Hamilton', 'Tauranga', 'Invercargill', 'New Plymouth', 'Napier',
                       'Dunedin', 'Henderson', 'Mount Wellington', 'Parnell', 'Takapuna',
                       'Onehunga', 'East Tamaki', 'Manukau', 'Matangi', 'Southland',
                       'Canterbury', 'Waikato', 'Bay of Plenty', 'Taranaki']
            location = ''
            for loc in nz_locs:
                if loc in after[:300]:
                    location = loc
                    break

            # Try to extract company name (between title and location)
            company = ''
            if location:
                loc_idx = after.find(location)
                between = after[:loc_idx].strip()
                # Company name is typically a short phrase
                if between and len(between) < 100:
                    company = between

            jobs.append({
                'title': job_title,
                'company': company,
                'location': location,
                'salary': salary,
                'link': link_href,
                'email_date': date,
                'email_subject': subject
            })

    # Also extract from plain text - find job blocks without links
    # SEEK emails list jobs in a structured format

    return jobs, subject, date


def deduplicate_jobs(all_jobs):
    """Remove duplicate jobs based on title+company+location."""
    seen = set()
    unique = []
    for job in all_jobs:
        key = f"{job.get('title', '')}|{job.get('company', '')}|{job.get('location', '')}"
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


# Process all email files
all_jobs = []
files = list(TOOL_DIR.glob("mcp-connector-proxy-qq-mail_GetMessage*.txt"))

for f in sorted(files):
    jobs, subject, date = parse_email_file(f)
    if jobs:
        all_jobs.extend(jobs)
        print(f"File: {f.name}")
        print(f"  Subject: {subject}")
        print(f"  Jobs found: {len(jobs)}")
        for j in jobs:
            print(f"    - {j['title']} | {j['company']} | {j['location']} | {j['salary']}")
    else:
        print(f"File: {f.name} - No jobs found from links, trying text extraction")
        # Fallback: extract from text patterns
        with open(f, 'r', encoding='utf-8') as fh:
            raw = fh.read()
        try:
            data = json.loads(raw)
            snippet = data.get('data', {}).get('data', {}).get('snippet', '')
            subject = data.get('data', {}).get('data', {}).get('subject', '')
            date = data.get('data', {}).get('data', {}).get('created_at', '')
        except:
            snippet = ''
            subject = ''
            date = ''

        # Parse snippet text for job entries
        # Snippet format: "Title  Company  Location  Salary"
        lines = snippet.split('\n')
        for line in lines:
            line = line.strip()
            if not line or 'Hi Wang' in line or 'Based on' in line or 'SEEK Limited' in line:
                continue

            # Check for salary
            sal_match = re.search(r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year))?', line)
            salary = sal_match.group() if sal_match else ''

            # Check for location
            nz_locs = ['Auckland CBD', 'Wellington Central', 'Christchurch Central',
                       'Hamilton Central', 'Tauranga Central', 'Invercargill Central',
                       'New Plymouth Central', 'Auckland', 'Wellington', 'Christchurch',
                       'Hamilton', 'Tauranga', 'Invercargill', 'New Plymouth', 'Henderson',
                       'Mount Wellington', 'Parnell', 'Takapuna', 'Onehunga',
                       'East Tamaki', 'Matangi', 'Southland', 'Canterbury', 'Waikato',
                       'Bay of Plenty', 'Taranaki']
            location = ''
            title_company = line
            for loc in nz_locs:
                if loc in line:
                    location = loc
                    idx = line.find(loc)
                    title_company = line[:idx].strip()
                    break

            if salary and title_company:
                # Remove salary from title_company
                title_company = re.sub(r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year))?', '', title_company).strip()

                # Try to split title and company
                # Company is often a distinct name after the title
                parts = title_company.split('  ')
                if len(parts) >= 2:
                    title = parts[0].strip()
                    company = parts[1].strip()
                else:
                    title = title_company
                    company = ''

                all_jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'link': '',
                    'email_date': date,
                    'email_subject': subject
                })

# Deduplicate
unique_jobs = deduplicate_jobs(all_jobs)

# Also add jobs from the SearchMessages snippets (the initial search result)
snippet_jobs = [
    # From msg_EuQYLPtByarAh6-_Kr7NkebOH-3wz50GKt-d5_ShD23NSQ (ICT, 6/22 21:47)
    {"title": "Project Business Analyst", "company": "PowerNet", "location": "Invercargill Central, Southland", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Data Analyst/Kaitātari Hoahoa", "company": "Stats NZ", "location": "Wellington Central, Wellington", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Business Analyst (6M Contract)", "company": "Sourced | IT Recruitment Specialists", "location": "Auckland CBD, Auckland", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    {"title": "Senior Business Analyst", "company": "Absol", "location": "", "salary": "", "link": "", "email_date": "2026-06-22T21:47:15Z"},
    # From msg_E1RuXnsden (ICT, 6/19 22:47)
    {"title": "Business Systems Analyst - ERP", "company": "Windsor Engineering Group Ltd", "location": "Mount Wellington, Auckland", "salary": "Competitive annual salary + employee benefits", "link": "", "email_date": "2026-06-19T22:47:15Z"},
    {"title": "System Analyst", "company": "Morgan Furniture Int Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-19T22:47:15Z"},
    {"title": "Graduate Functional Consultant", "company": "Credisense Limited", "location": "Auckland CBD, Auckland", "salary": "", "link": "", "email_date": "2026-06-19T22:47:15Z"},
    {"title": "Senior Technical Business Analyst", "company": "New Zealand Customs Service", "location": "Wellington Central, Wellington", "salary": "Competitive salary - in-house gym facility", "link": "", "email_date": "2026-06-19T22:47:15Z"},
    # From msg_7IyrJnTk (ICT, 6/21 21:47)
    {"title": "Business Analyst", "company": "New Plymouth District Council", "location": "New Plymouth Central, Taranaki", "salary": "", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    {"title": "Graduate Functional Consultant", "company": "Credisense Limited", "location": "Auckland CBD, Auckland", "salary": "", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    {"title": "Data Analyst", "company": "Frog Recruitment - Auckland", "location": "Auckland CBD, Auckland", "salary": "$40 per hour", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    {"title": "Senior Technical Business Analyst", "company": "New Zealand Customs Service", "location": "Wellington Central, Wellington", "salary": "Competitive salary - in-house gym facility", "link": "", "email_date": "2026-06-21T21:47:15Z"},
    # From msg_uffTTzevjWW (ICT, 6/18 21:47)
    {"title": "IT Support & AI Business Analyst", "company": "Miles Construction Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-18T21:47:15Z"},
    {"title": "Business Systems Analyst - ERP", "company": "Windsor Engineering Group Ltd", "location": "Mount Wellington, Auckland", "salary": "Competitive annual salary + employee benefits", "link": "", "email_date": "2026-06-18T21:47:15Z"},
    {"title": "System Analyst", "company": "Morgan Furniture Int Ltd", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-18T21:47:15Z"},
    {"title": "Technical BA", "company": "Techspace Consulting Limited", "location": "", "salary": "$40 per hour", "link": "", "email_date": "2026-06-18T21:47:15Z"},
    # From msg_o0mmZianwEnFiLKZtC9wrvfYJxWyoiDyPuSfkotNXpSkbA (Admin, 6/21 23:58)
    {"title": "Office Administrator / Manager", "company": "Simtec Therapeutic Limited", "location": "Onehunga, Auckland", "salary": "$65,000 – $85,000 per year", "link": "", "email_date": "2026-06-21T23:58:15Z"},
    {"title": "Office Manager", "company": "Finelawn Limited", "location": "Matangi, Waikato", "salary": "$75,000 – $90,000 per year + Bonus", "link": "", "email_date": "2026-06-21T23:58:15Z"},
    {"title": "Information Systems & Technology Support Analyst", "company": "Craigmore Corporate", "location": "Christchurch Central, Canterbury", "salary": "", "link": "", "email_date": "2026-06-21T23:58:15Z"},
    # From msg_EtdO_9gZsXMdEDN04xJvJ6i6wuVOdsqdieO75t2YnOzaFw (Admin, 6/22 23:58)
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Henderson, Auckland", "salary": "$51,000 per year", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    {"title": "Office Co-Ordinator", "company": "Flo & Frankie", "location": "Parnell, Auckland", "salary": "Competitive pay and great perks", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    {"title": "Office Manager", "company": "Fraundorfer Ltd", "location": "Tauranga Central, Bay of Plenty", "salary": "", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    {"title": "Finance & People Administrator (part-time)", "company": "Pie Funds Management Limited", "location": "Takapuna, Auckland", "salary": "", "link": "", "email_date": "2026-06-22T23:58:14Z"},
    # From msg_QCqvtvaIYH0PJ5KlUPukZUHrgAZx2lvFSRVawn_gsT4itQ (Admin, 6/18 23:58)
    {"title": "Entry Level Support Engineer", "company": "New Era Technology", "location": "Mount Wellington, Auckland", "salary": "$51,000 per year", "link": "", "email_date": "2026-06-18T23:58:15Z"},
    {"title": "Customer Service Administrator", "company": "Auckland RV Centre", "location": "East Tamaki, Auckland", "salary": "$25 – $30 per hour", "link": "", "email_date": "2026-06-18T23:58:15Z"},
    {"title": "Junior IT Sales and Support Technician", "company": "Computer Aid", "location": "Cambridge, Waikato", "salary": "", "link": "", "email_date": "2026-06-18T23:58:15Z"},
]

# Combine and deduplicate
all_jobs.extend(snippet_jobs)
unique_jobs = deduplicate_jobs(all_jobs)

# Sort by relevance (prioritize ICT and green-list jobs)
def job_sort_key(job):
    title = job.get('title', '').lower()
    # Priority categories for user
    if 'mechanical engineer' in title or 'erp' in title:
        return 0  # Highest: green list / core match
    if 'business system' in title or 'business analyst' in title:
        return 1  # High: BA/BSA
    if 'data analyst' in title:
        return 2  # Medium-high: data
    if 'it support' in title or 'information system' in title:
        return 3  # Medium: ICT support
    if 'system analyst' in title:
        return 4
    if 'functional consultant' in title:
        return 5
    if 'technical ba' in title or 'technical business' in title:
        return 6
    if 'office' in title or 'admin' in title:
        return 7  # Lower: admin
    return 8

unique_jobs.sort(key=job_sort_key)

# Output as JSON
output = json.dumps(unique_jobs, ensure_ascii=False, indent=2)
print(output)
print(f"\nTotal unique jobs: {len(unique_jobs)}")

# Save to file
output_path = Path(r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw.json")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"Saved to: {output_path}")
