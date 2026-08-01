#!/usr/bin/env python
"""Runner for process_seek_0730.py - injects the 8th email inline body."""
import json, sys, os

# Inject the inline body for the 8th email (ICT 13 from 7/28)
# This body was returned inline from QQ Mail GetMessage
INLINE_ICT13_BODY = r"""__BODY_WILL_BE_REPLACED__"""

# Save to JSON file for process_seek_0730.py to read
tool_dir = r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\36784eec-b585-49cd-9c1d-aefa8fee1097\tool-results"
inline_json_path = os.path.join(tool_dir, "inline_ict13_0728_body.json")

wrapper = {"data": {"data": {"body": INLINE_ICT13_BODY}}}
with open(inline_json_path, 'w', encoding='utf-8') as f:
    json.dump(wrapper, f, ensure_ascii=False)
print(f"Saved inline body to {inline_json_path}")

# Now run process_seek_0730.py
import process_seek_0730
# Override the FILES entry for the inline email to point to the saved JSON
for i, (path, ftype, label) in enumerate(process_seek_0730.FILES):
    if ftype == "inline":
        process_seek_0730.FILES[i] = (inline_json_path, "json", label)
        break

# Execute the main logic
if __name__ != "__main__":
    exec(open(os.path.join(os.path.dirname(__file__), "process_seek_0730.py")).read())
