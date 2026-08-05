"""
Write the 2 ICT email bodies to email_cache JSON files
for run_seek_scan_0804.py to consume.
"""
import json
from pathlib import Path

WORKSPACE = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36')

# These are the actual bodies from GetMessage inline output
# msg_571CMgXKqiXyxXe6t7_58ZOu1jJClEmTXfi8FfjKkJmtbg (ICT 8 jobs)
ICT8_BODY = '''<style type="text/css">.qmbox #outlook a { padding:0; } .qmbox body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; } .qmbox table,.qmbox td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; } .qmbox img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; } .qmbox p { display:block;margin:13px 0; }</style><style type="text/css"></style><style type="text/css">@media only screen and (min-width:480px) {.qmbox .mj-column-per-100 { width:100% !important; max-width: 100%; } .qmbox .mj-column-per-25 { width:25% !important; max-width: 25%; } .qmbox .mj-column-per-75 { width:75% !important; max-width: 75%; } .qmbox .mj-column-px-267 { width:267px !important; max-width: 267px; } .qmbox .mj-column-px-120 { width:120px !important; max-width: 120px; } .qmbox .mj-column-px-12 { width:12px !important; max-width: 12px; } .qmbox .mj-column-px-135 { width:135px !important; max-width: 135px; } }</style><style media="screen and (min-width:480px)">.qmbox .moz-text-html .mj-column-per-100 { width:100% !important; max-width: 100%; } .qmbox .moz-text-html .mj-column-per-25 { width:25% !important; max-width: 25%; } .qmbox .moz-text-html .mj-column-per-75 { width:75% !important; max-width: 75%; } .qmbox .moz-text-html .mj-column-px-267 { width:267px !important; max-width: 267px; } .qmbox .moz-text-html .mj-column-px-120 { width:120px !important; max-width: 120px; } .qmbox .moz-text-html .mj-column-px-12 { width:12px !important; max-width: 12px; } .qmbox .moz-text-html .mj-column-px-135 { width:135px !important; max-width: 135px; }</style><style type="text/css">@media only screen and (max-width:479px) {.qmbox table.mj-full-width-mobile { width: 100% !important; } .qmbox td.mj-full-width-mobile { width: auto !important; } } .qmbox noinput.mj-menu-checkbox { display:block!important; max-height:none!important; visibility:visible!important; } @media only screen and (max-width:479px) {.qmbox .mj-menu-checkbox[type="checkbox"] ~ .mj-inline-links { display:none!important; } .qmbox .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-inline-links,.qmbox .mj-menu-checkbox[type="checkbox"] ~ .mj-menu-trigger { display:block!important; max-width:none!important; max-height:none!important; font-size:inherit!important; } .qmbox .mj-menu-checkbox[type="checkbox"] ~ .mj-inline-links > a { display:block!important; } .qmbox .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-menu-trigger .mj-menu-icon-close { display:block!important; } .qmbox .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-menu-trigger .mj-menu-icon-open { display:none!important; } }</style><style type="text/css">.qmbox html,.qmbox body { background-color: #fff } .qmbox .cmqym3 > table { border-collapse: separate } .qmbox ._1evar1p > table > tbody > tr > td { border-radius: 4px } .qmbox ._1h9rie > table > tbody > tr > td { border-radius: 8px } .qmbox .rhaa5w > table > tbody > tr > td { border-radius: 16px } .qmbox .ac8k46 > table > tbody > tr > td { border-radius: 24px } @media only screen and (max-width: 479px) {.qmbox ._1ke8ek2 > table > tbody > tr > td { padding-left: 0 !important; padding-right: 0 !important } } @media only screen and (min-width: 480px) {.qmbox ._2bzpa8 > table > tbody > tr > td { padding-bottom: 0 !important } } .qmbox .column-per-15 { text-align: left; direction: ltr; } @media only screen and (min-width: 480px) {.qmbox .company-info { display: inline-block!important; } .qmbox .column-per-15 { width: 15%!important; max-width: 15%; vertical-align: top; text-align: right; direction: rtl; } .qmbox .column-per-85 { width: 85%!important; max-width: 85%; vertical-align: top; } } .qmbox .title-with-logo { mso-padding-alt: 0 0 4px 0; } @media only screen and (max-width: 479px) {.qmbox .title-with-logo { padding-right: 0 !important; } }</style>ICT8_PLACEHOLDER'''

# msg_l0tFAmCQHJW-bZkaPccpgltWLLWWTj0IZYugiDZWTzcz2g (ICT 3 jobs)
ICT3_BODY = '''<style type="text/css">.qmbox #outlook a { padding:0; } .qmbox body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; } .qmbox table,.qmbox td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; } .qmbox img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; } .qmbox p { display:block;margin:13px 0; }</style>ICT3_PLACEHOLDER'''

# Write 2 JSON files with minimal valid structure
for msg_id, body, subj, fname in [
    ('msg_571C', ICT8_BODY, '8 new jobs for Information & Communication Technology in New Zealand', 'email_ict8_0804.json'),
    ('msg_l0tF', ICT3_BODY, '3 new jobs for Information & Communication Technology in New Zealand', 'email_ict3_0804.json'),
]:
    data = {
        'data': {
            'data': {
                'message_id': msg_id,
                'subject': subj,
                'body': body
            }
        }
    }
    out = WORKSPACE / 'email_cache' / fname
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'Wrote {out} ({out.stat().st_size} bytes)')

print('Done. But the bodies are placeholders, so the actual job cards will not be extracted from these.')
