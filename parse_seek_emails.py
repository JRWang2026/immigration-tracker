#!/usr/bin/env python3
"""Parse SEEK job alert emails from QQ mail and extract structured job data."""
import os
import re
import json
from html.parser import HTMLParser
from pathlib import Path

TOOL_DIR = Path(r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\1c20b8bf-2fd1-42a9-b2d6-95331b066b4d\tool-results")

class SeekJobParser(HTMLParser):
    """Parse SEEK email HTML to extract job listings."""
    def __init__(self):
        super().__init__()
        self.jobs = []
        self.current_job = {}
        self.in_title = False
        self.in_company = False
        self.in_location = False
        self.in_salary = False
        self.in_link = False
        self.current_href = ""
        self.depth = 0
        self.text_buffer = ""
        self.all_text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        href = attrs_dict.get('href', '')
        style = attrs_dict.get('style', '')
        class_name = attrs_dict.get('class', '')

        # Detect job link (points to seek.co.nz/job/)
        if 'nz.seek.co.nz/job/' in href:
            self.in_link = True
            self.current_href = href
            self.current_job = {'link': href}

    def handle_endtag(self, tag):
        if self.in_link:
            self.in_link = False
            if self.current_job and 'title' not in self.current_job:
                title_text = self.text_buffer.strip()
                if title_text:
                    self.current_job['title'] = title_text
            self.text_buffer = ""

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.all_text_parts.append(text)
        if self.in_link:
            self.text_buffer += data


def extract_jobs_from_html(html_content):
    """Extract job data from SEEK email HTML content."""
    jobs = []

    # Method 1: Find job links and surrounding text
    job_link_pattern = re.compile(
        r'<a[^>]*href="(https://nz\.seek\.co\.nz/job/\d+[^"]*)"[^>]*>(.*?)</a>',
        re.DOTALL
    )

    # Find all job links
    for match in job_link_pattern.finditer(html_content):
        link = match.group(1)
        # Clean title - remove HTML tags
        title_raw = match.group(2)
        title = re.sub(r'<[^>]+>', '', title_raw).strip()
        if title and 'View' not in title and 'Apply' not in title:
            jobs.append({
                'title': title,
                'link': link
            })

    # Method 2: Extract structured blocks from text representation
    # SEEK emails have a pattern: Title Company Location Salary per line
    text = re.sub(r'<[^>]+>', '\n', html_content)
    text = re.sub(r'\s+', ' ', text)

    # Find salary patterns with context
    salary_pattern = re.compile(
        r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year|annum|month|week))?',
        re.IGNORECASE
    )

    # NZ location patterns
    nz_locations = [
        'Auckland CBD', 'Auckland', 'Wellington Central', 'Wellington',
        'Christchurch Central', 'Christchurch', 'Hamilton Central', 'Hamilton',
        'Tauranga Central', 'Tauranga', 'Dunedin', 'Invercargill Central',
        'Invercargill', 'New Plymouth Central', 'New Plymouth', 'Napier',
        'Whangarei', 'Rotorua', 'Nelson', 'Palmerston North', 'Hastings',
        'Mount Wellington', 'Mount Eden', 'Onehunga', 'East Tamaki',
        'Henderson', 'Parnell', 'Takapuna', 'Manukau', 'Southland',
        'Canterbury', 'Waikato', 'Bay of Plenty', 'Taranaki',
        'Hawke\'s Bay', 'Otago', 'Northland', 'Gisborne'
    ]

    return jobs, text, salary_pattern, nz_locations


def extract_jobs_from_snippets(snippets_data):
    """Extract jobs from the email search snippets (already have some text)."""
    all_jobs = []

    for item in snippets_data:
        snippet = item.get('snippet', '')
        subject = item.get('subject', '')
        msg_id = item.get('message_id', '')
        date = item.get('created_at', '')

        # Parse the snippet text for job entries
        # Pattern: "JobTitle  Company  Location  Salary"
        # Split by multiple spaces or newlines

        # Extract individual job lines from snippet
        lines = snippet.split('\n')
        current_job = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header/footer text
            if 'Hi Wang' in line or 'Based on your saved search' in line:
                continue
            if 'SEEK Limited' in line or 'registered user' in line:
                continue
            if 'we\'ve found' in line:
                continue

            # Check if line contains salary info
            salary_match = re.search(r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year))?', line)

            # Check if line looks like a job title (starts with capital letter, no $)
            if salary_match:
                salary = salary_match.group()
                # Remove salary from line to get remaining info
                remaining = line[:salary_match.start()].strip()
                if current_job:
                    current_job['salary'] = salary
                    # Try to parse remaining as location
                    for loc in ['Auckland CBD', 'Auckland', 'Wellington Central', 'Wellington',
                                'Christchurch Central', 'Christchurch', 'Hamilton', 'Tauranga',
                                'Invercargill', 'New Plymouth', 'Southland', 'Canterbury',
                                'Waikato', 'Bay of Plenty', 'Taranaki', 'Henderson',
                                'Mount Wellington', 'Parnell', 'Takapuna', 'Onehunga',
                                'East Tamaki', 'Matangi']:
                        if loc in remaining:
                            current_job['location'] = loc
                            break
                    all_jobs.append(current_job)
                    current_job = None
            else:
                # This might be a job title line
                # Check for NZ location
                found_loc = None
                for loc in ['Auckland CBD', 'Auckland', 'Wellington Central', 'Wellington',
                            'Christchurch Central', 'Christchurch', 'Hamilton', 'Tauranga',
                            'Invercargill Central', 'New Plymouth Central', 'Southland',
                            'Canterbury', 'Waikato', 'Bay of Plenty', 'Taranaki',
                            'Henderson', 'Mount Wellington', 'Parnell', 'Takapuna',
                            'Onehunga', 'East Tamaki', 'Matangi', 'Competitive',
                            'Invercargill', 'New Plymouth']:
                    if loc in line:
                        found_loc = loc
                        break

                if found_loc:
                    # Split: title + company before location
                    parts = line.split(found_loc)
                    title_company = parts[0].strip()
                    # Try to split title and company
                    # Company names often follow the title
                    current_job = {
                        'title_company': title_company,
                        'location': found_loc,
                        'source_date': date,
                        'email_subject': subject,
                        'msg_id': msg_id
                    }
                else:
                    # Could be just a title/company line
                    if len(line) > 3 and not line.startswith('Based') and not line.startswith('Hi'):
                        current_job = {
                            'title_company': line,
                            'source_date': date,
                            'email_subject': subject,
                            'msg_id': msg_id
                        }

    return all_jobs


# Process the saved email files
files = list(TOOL_DIR.glob("mcp-connector-proxy-qq-mail_GetMessage*.txt"))
print(f"Found {len(files)} email files to process")

for f in files:
    print(f"\nProcessing: {f.name}")
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()

    # Get job links
    links = re.findall(r'https://nz\.seek\.co\.nz/job/\d+', content)
    print(f"  Job links found: {len(links)}")

    # Get salary mentions
    salaries = re.findall(r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year|annum))?', content)
    print(f"  Salary mentions: {len(salaries)}")

    # Try to extract structured job blocks
    # SEEK emails use HTML tables/divs for each job
    # Find blocks that contain job title, company, location, salary together

    # Extract text between job-related patterns
    # Remove HTML tags first
    clean_text = re.sub(r'<[^>]+>', ' ', content)
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # Find job title patterns (known from snippets)
    known_titles = [
        'Business Systems Analyst - ERP',
        'Project Business Analyst',
        'Data Analyst',
        'Data Analyst/Kaitātari Hoahoa',
        'Business Analyst',
        'Senior Business Analyst',
        'Senior Technical Business Analyst',
        'IT Support & AI Business Analyst',
        'System Analyst',
        'Graduate Functional Consultant',
        'Entry Level Support Engineer',
        'Information Systems & Technology Support Analyst',
        'Office Administrator / Manager',
        'Office Manager',
        'Office Co-Ordinator',
        'Admin Support',
        'Finance & People Administrator',
        'Data Entry',
        'Junior IT Sales and Support Technician',
        'Technical BA',
        'Laboratory Assistant',
        'Research Technician',
        'Customer Service Administrator',
    ]

    for title in known_titles:
        if title in clean_text:
            # Find context around this title
            idx = clean_text.index(title)
            context = clean_text[idx:idx+300]
            # Try to extract company, location, salary from context
            # Pattern after title: CompanyName Location Salary
            after_title = context[len(title):].strip()

            # Find salary
            sal_match = re.search(r'\$[\d,]+(?:\s*[–\-]\s*\$?[\d,]+)?(?:\s+per\s+(?:hour|year|annum))?', after_title)
            salary = sal_match.group() if sal_match else ''

            # Find location
            loc_found = ''
            for loc in ['Auckland CBD', 'Auckland', 'Wellington Central', 'Wellington',
                        'Christchurch Central', 'Christchurch', 'Hamilton Central', 'Hamilton',
                        'Tauranga Central', 'Tauranga', 'Invercargill Central', 'Invercargill',
                        'New Plymouth Central', 'New Plymouth', 'Southland', 'Canterbury',
                        'Waikato', 'Bay of Plenty', 'Taranaki', 'Henderson',
                        'Mount Wellington', 'Parnell', 'Takapuna', 'Onehunga',
                        'East Tamaki', 'Matangi']:
                if loc in after_title[:200]:
                    loc_found = loc
                    break

            print(f"  FOUND: {title} | Loc: {loc_found} | Sal: {salary}")
