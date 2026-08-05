"""
SEEK NZ scan for 2026-08-04
4 unread SEEK emails:
  - msg_68aL (Admin, 20 jobs + 3 missed) -> email_cache/email_admin_0804.json
  - msg_571C (ICT 8 jobs + 3 missed)    -> inline body in script
  - msg__b4- (NZ General, 20 jobs + 3 missed) -> email_cache/email_nz_0804.json
  - msg_l0tF (ICT 3 jobs + 3 missed)    -> inline body in script
"""
import json, re, os, sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36')
sys.path.insert(0, str(WORKSPACE))
from local_agent.kos_bridge import write_kos_feed

# Load 2 file-based emails
file_paths = [
    (str(WORKSPACE / 'email_cache' / 'email_admin_0804.json'), 'json', 'Administration & Office Support'),
    (str(WORKSPACE / 'email_cache' / 'email_nz_0804.json'), 'json', 'NZ General'),
]

# Inline bodies for 2 ICT emails (manually pasted from earlier GetMessage output)
# msg_571C: ICT 8 jobs
ICT8_BODY = r'''{"data":{"data":{"message_id":"msg_571CMgXKqiXyxXe6t7_58ZOu1jJClEmTXfi8FfjKkJmtbg","body":"<style type=\"text/css\">.qmbox #outlook a { padding:0; } .qmbox body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; } .qmbox table,.qmbox td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; } .qmbox img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; } .qmbox p { display:block;margin:13px 0; } </style>MARKER_NO_JOBS_HERE_8JOBS_MARKER_END_NO_JOBS_HERE"}}'''

# msg_l0tF: ICT 3 jobs
ICT3_BODY = r'''{"data":{"data":{"message_id":"msg_l0tFAmCQHJW-bZkaPccpgltWLLWWTj0IZYugiDZWTzcz2g","body":"<style type=\"text/css\">MARKER_NO_JOBS_HERE_3JOBS_MARKER_END_NO_JOBS_HERE"}}'''

# Actually easier: extract from saved 571C + l0tF body via separate inline dicts
ICT8_BODY_INLINE = {
    'data': {
        'data': {
            'subject': '8 new jobs for Information & Communication Technology in New Zealand',
            'body': ''  # placeholder
        }
    }
}
ICT3_BODY_INLINE = {
    'data': {
        'data': {
            'subject': '3 new jobs for Information & Communication Technology in New Zealand',
            'body': ''  # placeholder
        }
    }
}

# Define a simple wrapper class to mimic file input
class BodyWrapper:
    def __init__(self, body):
        self._body = body
    def read(self):
        # Mock the read of a JSON file
        wrapper = {'data': {'data': {'body': self._body}}}
        return json.dumps(wrapper)

def load_body(path, ftype, body_override=None):
    if body_override is not None:
        return body_override
    with open(path, 'r', encoding='utf-8') as f:
        if ftype == 'json':
            data = json.load(f)
            return data['data']['data']['body']
        else:
            return f.read()

def extract_jobs(body):
    jobs = []
    card_pattern = r'<a style="display: block"'
    cards = body.split(card_pattern)

    for card in cards[1:]:
        title_match = re.search(r'text-decoration:underline[^>]*>([^<]+)</div>', card)
        company_match = re.search(r'font-size:14px;line-height:21px;padding-bottom:12px[^>]*>([^<]+)</td>', card)
        loc_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        salary_match = re.search(r'>\$[^<]+</div>', card)
        teaser_matches = re.findall(r'font-size:14px[^>]*line-height:21px[^>]*text-align:left[^>]*color:#2E3849[^>]*>([^<]+)</div>', card)
        date_match = re.search(r'Posted on (\d+ \w+ \d+)', card)
        url_match = re.search(r'href="([^"]+)"', card)

        title = title_match.group(1).strip() if title_match else None
        company = company_match.group(1).strip() if company_match else None

        if not title or not company or len(title) > 200:
            continue

        location = 'Unknown'
        for lm in loc_matches:
            lm = lm.strip()
            if ',' in lm and lm not in [title, company]:
                location = lm
                break
            elif lm and lm not in [title, company] and not location.replace('Unknown', ''):
                location = lm

        salary = ''
        if salary_match:
            salary = salary_match.group(0).replace('>', '').replace('</div>', '').strip()
        elif teaser_matches:
            for tm in teaser_matches:
                tm = tm.strip()
                if tm and tm != location and tm not in [title, company] and ',' not in tm:
                    if not re.match(r'^\d+ \w+ \d+$', tm):
                        salary = tm
                        break

        if not salary:
            for tm in teaser_matches:
                tm = tm.strip()
                if tm and tm != location and tm not in [title, company]:
                    if re.search(r'(competitive|benefits|insurance|super|bonus|market)', tm, re.I):
                        salary = tm
                        break

        posted_date = date_match.group(1) if date_match else ''
        url = url_match.group(1) if url_match else ''

        import html
        title = html.unescape(title)
        company = html.unescape(company)
        location = html.unescape(location)
        salary = html.unescape(salary).replace('</div', '').strip()

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'posted_date': posted_date,
            'url': url,
            'source': '',
        })
    return jobs

# We will not load inline ICT emails here, since the JSON files cover all 4 batches via dedup.
# But the ICT 8 jobs email includes some unique jobs (Senior Adviser AMR Technical, etc.) not in Admin/NZ General.
# Let me handle them by reading the tool-results for the 2 small emails directly.

# Use saved GetMessage tool-results directly
TOOL_RESULTS_DIR = Path(r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\1ab8c74e-745d-43d8-8152-bb294029f3af\tool-results')

# Read all 4 message files - we need to discover them. The 2 big ones were already saved
# (4b8a5e, 658b17). The 2 small ones (571C, l0tF) were returned inline.
# Since we already have inline content, let me just use the 2 large files we have,
# but also add the 2 small inline ones from the conversation above.

# Better approach: read everything in the call_function files (tool internal output)
all_files = sorted(TOOL_RESULTS_DIR.glob('call_function_*.txt'))
print('Tool internal files:')
for f in all_files:
    print(f'  {f.name} ({f.stat().st_size} bytes)')

# Use the 2 large files + manually-constructed inline for 2 small ones
# Easiest: use the JSON files we have for Admin + NZ General
# For the 2 small ICT emails, the data is in the call_function files (which contain the
# tool call results, not the message bodies). The message bodies are in the GetMessage outputs.
# Since 2 small ICT emails came back inline successfully, write them to email_cache.

ICT8_JSON_PATH = WORKSPACE / 'email_cache' / 'email_ict8_0804.json'
ICT3_JSON_PATH = WORKSPACE / 'email_cache' / 'email_ict3_0804.json'

# Construct the JSON files for the 2 ICT emails (from the previous GetMessage output)
ICT8_DATA = {
    "data": {
        "data": {
            "message_id": "msg_571CMgXKqiXyxXe6t7_58ZOu1jJClEmTXfi8FfjKkJmtbg",
            "subject": "8 new jobs for Information & Communication Technology in New Zealand",
            "body": "__BODY_PLACEHOLDER__"
        }
    }
}
ICT3_DATA = {
    "data": {
        "data": {
            "message_id": "msg_l0tFAmCQHJW-bZkaPccpgltWLLWWTj0IZYugiDZWTzcz2g",
            "subject": "3 new jobs for Information & Communication Technology in New Zealand",
            "body": "__BODY_PLACEHOLDER__"
        }
    }
}

# Save the JSON for the 2 small ICT emails
with open(ICT8_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(ICT8_DATA, f, ensure_ascii=False)
with open(ICT3_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(ICT3_DATA, f, ensure_ascii=False)

print('Placeholder JSON files created. Now updating with actual bodies...')

