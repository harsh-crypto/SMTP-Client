# Gmail SMTP Client

Send emails from your Gmail account via SMTP. Designed to be embedded or scripted for future automation (scheduled sends, triggers, etc.).

## Setup

1. Enable 2-Step Verification on your Google account: https://myaccount.google.com/security
2. Create an App Password: https://myaccount.google.com/apppasswords (choose "Mail")
3. Copy `.env.example` to `.env` and fill in:
   ```
   GMAIL_ADDRESS=youremail@gmail.com
   GMAIL_APP_PASSWORD=your-16-char-app-password
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

CLI:
```
python send_email.py --to someone@example.com --subject "Hi" --body "Hello there"
python send_email.py --to a@x.com,b@y.com --subject "Report" --body-file report.html --html --attach data.csv
```

Programmatic use (for future automation):
```python
from gmail_client import GmailClient

client = GmailClient()
client.send(
    to="someone@example.com",
    subject="Automated alert",
    body="Service check failed at 03:00.",
    attachments=["logs.txt"],
)
```

## Notes

- Uses SMTP over SSL on port 465 (Gmail standard).
- Credentials come from `.env` — never commit `.env` (it is gitignored).
- Regular Gmail account passwords will not work; you must use an App Password.
