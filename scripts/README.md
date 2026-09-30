# Scripts

Helper scripts for this project.

## `generate_vapid_keys.py` — Web Push (VAPID) key generation

Generates a real VAPID (RFC 8292) key pair for the Web Push notification
feature (see `database/push_notify.py`, `database/push_subscriptions_store.py`,
`api/main.py` `/push/*` endpoints). VAPID is a **self-generated** key pair -
no third-party account, signup, or API key is needed (unlike the older
FCM/APNs-only approach).

Run once per environment (dev and prod should each have their own pair),
from the project root with the virtual environment set up:

```powershell
venv\Scripts\python.exe scripts\generate_vapid_keys.py
```

This prints three lines - copy them into your local `.env` (never commit
`.env`, see `.gitignore`):

```
VAPID_PUBLIC_KEY=...
VAPID_PRIVATE_KEY=...
VAPID_CLAIMS_EMAIL=mailto:you@example.com
```

Replace `VAPID_CLAIMS_EMAIL` with a real contact address you control - RFC
8292 requires it (push services may use it to reach you about abuse).

Without these three variables set, `GET /push/vapid-public-key` honestly
returns 503 ("VAPID anahtarları henüz üretilmedi") instead of a fake key,
and `database/push_notify.py` logs that it's skipping the send rather than
pretending to have sent a notification - see that module's docstring.
