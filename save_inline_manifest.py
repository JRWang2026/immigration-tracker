"""
Save the 2 SEEK emails that were returned inline as JSON files
in the same format as the tool-results directory.
The bodies were fetched via mcp__qq-mail__GetMessage earlier.
"""
import json
import re
from pathlib import Path

CACHE = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\email_cache_seek_0808')

# Aug 7 ICT 10 jobs - body extracted from the inline API response (94K chars)
# msg_mEgcFJlfydgolWOQNOqtlbpaR1ci0la9rE22gm5dPD_Wvw
# Aug 6 ICT 13 jobs - body extracted from inline API response (97K chars)
# msg_KV3ZQo-j4TDct9-6blhtwA5PC16rQEPd0dyqgRsTU_jtzw

# We will use the actual tool-results files we already copied
# and put a manifest that says where each email is.
# But to be safe, also create synthetic stubs for the inline ones.

# Actually a cleaner approach: just re-fetch the message bodies when running the script,
# using the body content from the tool-results files in the local cache directory.

# For now, write a manifest that just records the metadata for the inline emails
manifest = [
    {
        "file": None,  # inline only - parsed at runtime
        "label": "msg_mEgcFJlfydgolWOQNOqtlbpaR1ci0la9rE22gm5dPD_Wvw",
        "subject": "10 new jobs for Information & Communication Technology in New Zealand",
        "created_at": "2026-08-07T21:25:32Z",
        "size_hint": "10 jobs ICT (Aug 7 21:25 UTC)",
    },
    {
        "file": None,
        "label": "msg_KV3ZQo-j4TDct9-6blhtwA5PC16rQEPd0dyqgRsTU_jtzw",
        "subject": "13 new jobs for Information & Communication Technology in New Zealand",
        "created_at": "2026-08-06T20:25:33Z",
        "size_hint": "13 jobs ICT (Aug 6 20:25 UTC)",
    },
]

with open(CACHE / 'inline_email_manifest.json', 'w', encoding='utf-8') as f:
    json.dump({'inline_messages': manifest}, f, ensure_ascii=False, indent=2)

print(f"Manifest written to {CACHE / 'inline_email_manifest.json'}")
