import json, re

# Parse Admin email (20 new jobs)
with open(r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\0929370e-8eb6-4e33-8470-d6431d495fca\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782615179978-b89936.txt', 'r', encoding='utf-8') as f:
    data1 = json.load(f)
body1 = data1['data']['data']['body']

# Parse ICT email (19 new jobs)
with open(r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\0929370e-8eb6-4e33-8470-d6431d495fca\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782615180099-250eca.txt', 'r', encoding='utf-8') as f:
    data2 = json.load(f)
body2 = data2['data']['data']['body']

def extract_jobs_from_seek_email(body):
    # Extract job blocks between href links
    # Each job card has: title (underline div), company, location, salary/teaser
    results = []

    # Find all job card sections
    # Titles are in divs with text-decoration:underline
    titles = re.findall(r'text-decoration:underline[^>]*>([^<]+)</div>', body)
    # Companies follow the title in a td
    companies = re.findall(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', body)
    # Locations
    loc_pattern = r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>'
    locations_raw = re.findall(loc_pattern, body)

    # Filter locations - keep only those with comma (City, Region pattern)
    locations = [l for l in locations_raw if ',' in l or l.strip() in ['Auckland', 'Wellington', 'Canterbury', 'Waikato', 'Christchurch']]

    # Salaries
    salaries = re.findall(r'>\$[^<]+</div>', body)
    salaries_clean = [s.replace('>','').replace('</div>','').strip() for s in salaries]

    # Posted dates
    dates = re.findall(r'Posted on (\d+ \w+ \d+)', body)

    # Now build structured job list
    # We need to parse the HTML more carefully to associate title+company+location+salary
    # Split by job card anchors
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:  # skip first which is before first card
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        loc_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)

        # Salary - look for dollar amounts or teaser text
        salary_match = re.search(r'>\$[^<]+</div>', card)
        # Also look for non-salary teaser text (benefits etc)
        teaser_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)

        # Posted date
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)

        title = title_match.group(1).strip() if title_match else 'Unknown'
        company = company_match.group(1).strip() if company_match else 'Unknown'

        # Location: first location match that has comma pattern
        location = 'Unknown'
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm:
                location = lm
                break
            elif lm and lm not in company:
                location = lm
                break

        # Salary or teaser
        salary = ''
        if salary_match:
            salary = salary_match.group(0).replace('>','').replace('</div>','').strip()
        elif teaser_matches:
            # Find teaser that's not the location
            for tm in teaser_matches:
                tm = tm.strip()
                if tm != location and tm not in ['Unknown', company] and ',' not in tm:
                    salary = tm
                    break

        posted_date = date_match.group(1) if date_match else ''

        results.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': posted_date,
        })

    return results

jobs_admin = extract_jobs_from_seek_email(body1)
jobs_ict = extract_jobs_from_seek_email(body2)

print(f"=== Admin Email (20 new jobs) - Extracted {len(jobs_admin)} ===")
for j in jobs_admin:
    print(f"  {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['posted_date']}")

print()
print(f"=== ICT Email (19 new jobs) - Extracted {len(jobs_ict)} ===")
for j in jobs_ict:
    print(f"  {j['title']} | {j['company']} | {j['location']} | {j['salary']} | {j['posted_date']}")
