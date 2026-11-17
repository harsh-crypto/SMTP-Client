import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEFAULT_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
DEFAULT_PORT = int(os.getenv("SMTP_PORT", "465"))


class GmailClient:
    def __init__(self, address: str = None, password: str = None, host: str = None, port: int = None):
        self.address = address or os.getenv("GMAIL_ADDRESS")
        self.password = password or os.getenv("GMAIL_APP_PASSWORD")
        self.host = host or DEFAULT_HOST
        self.port = port or DEFAULT_PORT
        if not self.address or not self.password:
            raise ValueError(
                "GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set "
                "(in environment or .env file)."
            )

    def send(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        cc: str | list[str] = None,
        bcc: str | list[str] = None,
        attachments: list[str] = None,
        html: bool = False,
    ) -> str:
        msg = EmailMessage()
        msg["From"] = self.address
        msg["To"] = ", ".join(self._as_list(to))
        if cc:
            msg["Cc"] = ", ".join(self._as_list(cc))
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        hidden = self._as_list(bcc) if bcc else []
        all_recipients = self._as_list(to) + self._as_list(cc) + hidden

        content_type = "html" if html else "plain"
        msg.set_content(body, subtype=content_type)

        for path in attachments or []:
            file = Path(path)
            if not file.is_file():
                raise FileNotFoundError(f"Attachment not found: {file}")
            data = file.read_bytes()
            ctype = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
            maintype, _, subtype = ctype.partition("/")
            msg.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=file.name,
            )

        self._deliver(msg, all_recipients)
        return msg["To"]

    def _deliver(self, msg: EmailMessage, recipients: list[str]) -> None:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
            server.login(self.address, self.password)
            server.send_message(msg)

    @staticmethod
    def _as_list(value: str | list[str]) -> list[str]:
        if value is None:
            return []
        return [v.strip() for v in value.split(",")] if isinstance(value, str) else list(value)
