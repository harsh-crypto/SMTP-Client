import os
import poplib
import ssl
import sys
from email import message_from_bytes
from email.header import decode_header
from email.message import EmailMessage, Message

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

DEFAULT_HOST = os.getenv("POP_HOST", "pop.gmail.com")
DEFAULT_PORT = int(os.getenv("POP_PORT", "995"))


class PopClient:
    def __init__(self, address: str = None, password: str = None, host: str = None, port: int = None, recent: bool = False):
        self.address = address or os.getenv("GMAIL_ADDRESS")
        self.password = password or os.getenv("GMAIL_APP_PASSWORD")
        if recent:
            self.address = f"recent:{self.address}"
        self.host = host or DEFAULT_HOST
        self.port = port or DEFAULT_PORT
        if not self.address or not self.password:
            raise ValueError(
                "GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set "
                "(in environment or .env file)."
            )

    def __enter__(self):
        context = ssl.create_default_context()
        self._server = poplib.POP3_SSL(self.host, self.port, context=context)
        self._server.user(self.address)
        self._server.pass_(self.password)
        return self

    def __exit__(self, *exc):
        if getattr(self, "_server", None):
            try:
                self._server.quit()
            except Exception:
                pass

    def list_messages(self, limit: int = 10) -> list[dict]:
        count, _ = self._server.stat()
        start = max(1, count - limit + 1)
        items = []
        for num in range(start, count + 1):
            _, headers, _ = self._server.top(num, 0)
            msg = message_from_bytes(b"\n".join(headers))
            items.append({
                "num": num,
                "from": self._decode(msg["From"]),
                "subject": self._decode(msg["Subject"]),
                "date": self._decode(msg["Date"]),
            })
        return items

    def fetch(self, num: int, save_dir: str = None) -> EmailMessage:
        _, lines, __ = self._server.retr(num)
        msg = message_from_bytes(b"\n".join(lines))

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            for part in msg.walk():
                filename = part.get_filename()
                if filename:
                    with open(os.path.join(save_dir, self._decode(filename)), "wb") as f:
                        f.write(part.get_payload(decode=True) or b"")

        return msg

    def fetch_latest(self, n: int = 5) -> list[EmailMessage]:
        count, _ = self._server.stat()
        start = max(1, count - n + 1)
        return [self.fetch(num) for num in range(start, count + 1)]

    def get_body(self, msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get_filename():
                    return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
            return ""
        payload = msg.get_payload(decode=True)
        return payload.decode(msg.get_content_charset() or "utf-8", errors="replace") if payload else ""

    @staticmethod
    def _decode(value) -> str:
        if value is None:
            return ""
        parts = decode_header(value)
        decoded = []
        for text, charset in parts:
            if isinstance(text, bytes):
                decoded.append(text.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(text)
        return "".join(decoded)
