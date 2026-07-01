#!/usr/bin/env python3
"""Parse SEEK NZ job alert emails from saved QQ Mail connector output files."""

import json
import re
import os
from html.parser import HTMLParser

# File paths for the 3 newest emails
EMAIL_FILES = {
    "ict_0626_2247": r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\14ce4fcf-9543-4fa8-b1cf-791418539882\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782542091668-5b6321.txt",
    "ict_0626_2125": r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\14ce4fcf-9543-4fa8-b1cf-791418539882\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782542091554-5f4983.txt",
    "admin_0627": r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\14ce4fcf-9543-4fa8-b1cf-791418539882\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782542091612-304d6c.txt",
}

class SEEKJobParser(HTMLParser):
    """Extract job listings from SEEK email HTML."""
    
    def __init__(self):
        super().__init__()
        self.jobs = []
        self.current_job = {}
        self.in_title = False
        self.in_company = False
        self.in_location = False
        self.in_salary = False
        self.in_link = False
        self.current_link = ""
        self.in_text_block = False
        self.depth = 0
        self.raw_text = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Detect job link (href containing seek.co.nz/job)
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if '/job/' in href or 'seek.co.nz' in href and '/job' in href:
                self.in_link = True
                self.current_link = href
        
    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_link = False
            
    def handle_data(self, data):
        self.raw_text += data


def extract_jobs_from_raw_text(raw_text):
    """Extract job information from the raw text content of SEEK emails."""
    jobs = []
    
    # Split by common job separators
    # SEEK emails typically have pattern: Title | Company | Location | Salary
    # Let's find job links first to identify job blocks
    
    # Find all SEEK job URLs
    job_urls = re.findall(r'https?://(?:email\.s\.seek\.co\.nz|nz\.seek\.co\.nz)/[^"\s<>]+/job/\d+', raw_text)
    
    # Alternative: find job IDs
    job_ids = re.findall(r'/job/(\d+)', raw_text)
    
    # Extract structured text between markers
    # Remove HTML tags for cleaner text
    clean_text = re.sub(r'<[^>]+>', ' ', raw_text)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # Find salary patterns
    salaries = re.findall(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s+per\s+(?:year|hour|annum))?', clean_text)
    
    return {
        'job_ids': job_ids,
        'job_urls': job_urls,
        'salaries': salaries,
        'clean_text_preview': clean_text[:3000],
    }


def parse_email_file(filepath):
    """Parse a single email file and extract job data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse JSON structure
    try:
        data = json.loads(content)
        body = data['data']['data']['body']
        subject = data['data']['data']['subject']
        created_at = data['data']['data']['created_at']
    except (json.JSONDecodeError, KeyError):
        # Try reading as raw text
        body = content
        subject = "Unknown"
        created_at = "Unknown"
    
    # Clean HTML - remove tags, get text
    clean = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    clean = re.sub(r'<script[^>]*>.*?</script>', '', clean, flags=re.DOTALL)
    clean = re.sub(r'<[^>]+>', '\n', clean)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'&amp;', '&', clean)
    clean = re.sub(r'&#\d+;', '', clean)
    clean = re.sub(r'\n\s*\n', '\n', clean)
    clean = clean.strip()
    
    # Extract job listings
    # Pattern: job title, then company, location, salary on following lines
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    
    # Find job blocks by looking for salary patterns or location patterns
    jobs = []
    current_title = None
    current_company = None
    current_location = None
    current_salary = None
    current_link = None
    
    # Extract all job URLs from body
    all_links = re.findall(r'href="(https?://[^"]+)"', body)
    seek_job_links = [l for l in all_links if '/job/' in l]
    
    # Better approach: find job blocks in the text
    # SEEK emails format: Title followed by Company, Location, Salary
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this looks like a job title (short, no salary, no location pattern)
        salary_match = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s+per\s+(?:year|hour|annum))?', line)
        location_match = re.search(r'(Auckland|Wellington|Christchurch|Hamilton|Tauranga|Rotorua|Invercargill|New Plymouth|Waikato|Bay of Plenty|Canterbury|Southland|Taranaki|Waikato|Hawke\'s Bay|Otago|Manawatu|Northland|Gisborne|Marlborough|Nelson|West Coast)', line, re.IGNORECASE)
        
        # Skip non-job lines
        skip_patterns = ['Hi Wang', 'Based on your saved search', 'we\'ve found', 'new jobs', 
                        'SEEK', 'View all', 'Update your', '© SEEK', 'Cremorne', 
                        'unsubscribe', 'privacy', 'We\'re here', 'Don\'t miss',
                        'Could be right', 'Jobs you may have missed',
                        'Update', 'Saved search', 'View', 'manage']
        
        is_skip = any(p.lower() in line.lower() for p in skip_patterns)
        
        if not is_skip and len(line) > 3 and not salary_match and not location_match and len(line) < 80:
            # This might be a job title
            # Check if next lines contain company/location/salary
            potential_company = lines[i+1] if i+1 < len(lines) else None
            potential_location = lines[i+2] if i+2 < len(lines) else None
            
            if potential_company and len(potential_company) < 60 and not re.search(r'\$', potential_company):
                current_title = line
                current_company = potential_company
                
                # Look for location in next few lines
                for j in range(i+2, min(i+5, len(lines))):
                    loc_m = re.search(r'([\w\s]+,\s*(Auckland|Wellington|Christchurch|Hamilton|Tauranga|Rotorua|Invercargill|New Plymouth|Waikato|Bay of Plenty|Canterbury|Southland|Taranaki))', lines[j], re.IGNORECASE)
                    if loc_m:
                        current_location = loc_m.group(0)
                        # Check same line for salary
                        sal_m = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s+per\s+(?:year|hour|annum))?', lines[j])
                        if sal_m:
                            current_salary = sal_m.group(0)
                        break
                    # Check for salary alone
                    sal_m = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s+per\s+(?:year|hour|annum))?', lines[j])
                    if sal_m and not current_salary:
                        current_salary = sal_m.group(0)
                
                # Also check if company line contains location  
                if not current_location:
                    loc_in_company = re.search(r'([\w\s]+,\s*(Auckland|Wellington|Christchurch|Hamilton|Tauranga|Rotorua|Invercargill|New Plymouth|Waikato|Bay of Plenty|Canterbury|Southland|Taranaki))', potential_company, re.IGNORECASE)
                    if loc_in_company:
                        current_location = loc_in_company.group(0)
                
                if current_title:
                    jobs.append({
                        'title': current_title,
                        'company': current_company or '',
                        'location': current_location or '',
                        'salary': current_salary or '',
                        'link': '',
                    })
                    current_title = None
                    current_company = None
                    current_location = None
                    current_salary = None
        
        i += 1
    
    return {
        'subject': subject,
        'created_at': created_at,
        'jobs': jobs,
        'seek_job_links': seek_job_links,
        'clean_lines_count': len(lines),
    }


def main():
    all_results = {}
    all_jobs = []
    
    for key, filepath in EMAIL_FILES.items():
        try:
            result = parse_email_file(filepath)
            all_results[key] = result
            all_jobs.extend(result['jobs'])
            print(f"\n=== {key} ===")
            print(f"Subject: {result['subject']}")
            print(f"Date: {result['created_at']}")
            print(f"Jobs extracted: {len(result['jobs'])}")
            for j in result['jobs']:
                print(f"  - {j['title']} | {j['company']} | {j['location']} | {j['salary']}")
        except Exception as e:
            print(f"Error parsing {key}: {e}")
            all_results[key] = {'error': str(e)}
    
    # Deduplicate jobs
    seen = set()
    deduped = []
    for j in all_jobs:
        key = f"{j['title']}|{j['company']}"
        if key not in seen:
            seen.add(key)
            deduped.append(j)
    
    print(f"\n=== DEDUPED TOTAL: {len(deduped)} ===")
    
    # Save raw results for further processing
    output = {
        'all_results': all_results,
        'deduped_jobs': deduped,
    }
    
    outpath = r"C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\seek_jobs_raw_0627.json"
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {outpath}")
    return deduped


if __name__ == '__main__':
    main()
