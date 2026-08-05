"""
Save the 2 ICT email bodies (from inline GetMessage results) to email_cache
"""
import json
from pathlib import Path

WORKSPACE = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36')

# msg_571C body (8 ICT jobs + 3 missed)
ICT8_BODY = r'''<style type="text/css">.qmbox #outlook a { padding:0; } .qmbox body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; } .qmbox table,.qmbox td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; } .qmbox img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; } .qmbox p { display:block;margin:13px 0; }</style><style type="text/css"></style><style type="text/css">@media only screen and (min-width:480px) {.qmbox .mj-column-per-100 { width:100% !important; max-width: 100%; } .qmbox .mj-column-per-25 { width:25% !important; max-width: 25%; } .qmbox .mj-column-per-75 { width:75% !important; max-width: 75%; } .qmbox .mj-column-px-267 { width:267px !important; max-width: 267px; } .qmbox .mj-column-px-120 { width:120px !important; max-width: 120px; } .qmbox .mj-column-px-12 { width:12px !important; max-width: 12px; } .qmbox .mj-column-px-135 { width:135px !important; max-width: 135px; } }</style><style media="screen and (min-width:480px)">.qmbox .moz-text-html .mj-column-per-100 { width:100% !important; max-width: 100%; } .qmbox .moz-text-html .mj-column-per-25 { width:25% !important; max-width: 25%; } .qmbox .moz-text-html .mj-column-per-75 { width:75% !important; max-width: 75%; } .qmbox .moz-text-html .mj-column-px-267 { width:267px !important; max-width: 267px; } .qmbox .moz-text-html .mj-column-px-120 { width:120px !important; max-width: 120px; } .qmbox .moz-text-html .mj-column-px-12 { width:12px !important; max-width: 12px; } .qmbox .moz-text-html .mj-column-px-135 { width:135px !important; max-width: 135px; }</style><style type="text/css">@media only screen and (max-width:479px) {.qmbox table.mj-full-width-mobile { width: 100% !important; } .qmbox td.mj-full-width-mobile { width: auto !important; } } .qmbox noinput.mj-menu-checkbox { display:block!important; max-height:none!important; visibility:visible!important; } @media only screen and (max-width:479px) {.qmbox .mj-menu-checkbox[type="checkbox"] ~ .mj-inline-links { display:none!important; } .qmbox .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-inline-links,.qmbox .mj-menu-checkbox[type="checkbox"] ~ .mj-menu-trigger { display:block!important; max-width:none!important; max-height:none!important; font-size:inherit!important; } .qmbox .mj-menu-checkbox[type="checkbox"] ~ .mj-inline-links &gt; a { display:block!important; } .qmbox .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-menu-trigger .mj-menu-icon-close { display:block!important; } .qmbox .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-menu-trigger .mj-menu-icon-open { display:none!important; } }</style><style type="text/css">.qmbox html,.qmbox body { background-color: #fff } .qmbox .cmqym3 &gt; table { border-collapse: separate } .qmbox ._1evar1p &gt; table &gt; tbody &gt; tr &gt; td { border-radius: 4px } .qmbox ._1h9rie &gt; table &gt; tbody &gt; tr &gt; td { border-radius: 8px } .qmbox .rhaa5w &gt; table &gt; tbody &gt; tr &gt; td { border-radius: 16px } .qmbox .ac8k46 &gt; table &gt; tbody &gt; tr &gt; td { border-radius: 24px } @media only screen and (max-width: 479px) {.qmbox ._1ke8ek2 &gt; table &gt; tbody &gt; tr &gt; td { padding-left: 0 !important; padding-right: 0 !important } } @media only screen and (min-width: 480px) {.qmbox ._2bzpa8 &gt; table &gt; tbody &gt; tr &gt; td { padding-bottom: 0 !important } } .qmbox .column-per-15 { text-align: left; direction: ltr; } @media only screen and (min-width: 480px) {.qmbox .company-info { display: inline-block!important; } .qmbox .column-per-15 { width: 15%!important; max-width: 15%; vertical-align: top; text-align: right; direction: rtl; } .qmbox .column-per-85 { width: 85%!important; max-width: 85%; vertical-align: top; } } .qmbox .title-with-logo { mso-padding-alt: 0 0 4px 0; } @media only screen and (max-width: 479px) {.qmbox .title-with-logo { padding-right: 0 !important; } }</style>ICT8_BODY_MARKER'''

# msg_l0tF body (3 ICT jobs + 3 missed)
ICT3_BODY = r'''<style type="text/css">.qmbox #outlook a { padding:0; } .qmbox body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; } .qmbox table,.qmbox td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; } .qmbox img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; } .qmbox p { display:block;margin:13px 0; }</style>ICT3_BODY_MARKER'''

# Actually, the best approach is to load the inline bodies directly from the tool-results
# call_function files which contain the original tool call output

TOOL_RESULTS_DIR = Path(r'C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\1ab8c74e-745d-43d8-8152-bb294029f3af\tool-results')

# Read call_function_2.txt which should contain the 3rd call (probably ICT 3 jobs)
for f in TOOL_RESULTS_DIR.glob('call_function_*.txt'):
    print(f'Reading {f.name} ({f.stat().st_size} bytes)')
    content = f.read(encoding='utf-8', errors='ignore')
    if 'devops' in content.lower() or 'sre' in content.lower() or 'techspace' in content.lower():
        # This is likely the ICT email
        # Try to extract the body
        import re
        # Look for body field
        body_m = re.search(r'"body":\s*"((?:[^"\\]|\\.)*)"', content)
        if body_m:
            print(f'  Found body field, length: {len(body_m.group(1))}')
        # Look for any text
        if 'display: block' in content:
            # Count cards
            count = content.count('<a style="display: block"')
            print(f'  Found {count} job cards')
        # Check subject
        subj_m = re.search(r'"subject":\s*"([^"]+)"', content)
        if subj_m:
            print(f'  Subject: {subj_m.group(1)}')
