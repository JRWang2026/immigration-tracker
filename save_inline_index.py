import json
from pathlib import Path

cache_dir = Path(r'C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\email_cache_seek_0808')
cache_dir.mkdir(parents=True, exist_ok=True)

email_aug7_ict10 = {
    "message_id": "msg_mEgcFJlfydgolWOQNOqtlbpaR1ci0la9rE22gm5dPD_Wvw",
    "subject": "10 new jobs for Information & Communication Technology in New Zealand",
    "created_at": "2026-08-07T21:25:32Z",
    "type": "10_jobs_ict_aug7"
}

email_aug6_ict13 = {
    "message_id": "msg_KV3ZQo-j4TDct9-6blhtwA5PC16rQEPd0dyqgRsTU_jtzw",
    "subject": "13 new jobs for Information & Communication Technology in New Zealand",
    "created_at": "2026-08-06T20:25:33Z",
    "type": "13_jobs_ict_aug6"
}

with open(cache_dir / 'inline_email_index.json', 'w', encoding='utf-8') as f:
    json.dump({'emails': [email_aug7_ict10, email_aug6_ict13]}, f, ensure_ascii=False, indent=2)

print(f"Created cache at {cache_dir}")
print(f"Index written to {cache_dir / 'inline_email_index.json'}")
