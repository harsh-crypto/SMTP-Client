import unittest
from unittest.mock import patch, MagicMock
from gmail_client import GmailClient


class GmailClientTests(unittest.TestCase):
    def make_client(self):
        return GmailClient(address="test@gmail.com", password="app-password")

    @patch("gmail_client.smtplib.SMTP_SSL")
    def test_send_plain(self, smtp_cls):
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server
        client = self.make_client()
        client.send(to="a@example.com", subject="Hi", body="Hello")
        server.login.assert_called_once_with("test@gmail.com", "app-password")
        msg = server.send_message.call_args[0][0]
        self.assertEqual(msg["To"], "a@example.com")
        self.assertEqual(msg["Subject"], "Hi")
        self.assertEqual(msg["From"], "test@gmail.com")

    @patch("gmail_client.smtplib.SMTP_SSL")
    def test_send_multi_recipient_html(self, smtp_cls):
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server
        client = self.make_client()
        client.send(to="a@example.com,b@example.com", subject="S",
                    body="<b>x</b>", cc="c@example.com", html=True)
        msg = server.send_message.call_args[0][0]
        self.assertEqual(msg["To"], "a@example.com, b@example.com")
        self.assertEqual(msg["Cc"], "c@example.com")
        self.assertEqual(msg.get_content_type(), "text/html")

    @patch("gmail_client.smtplib.SMTP_SSL")
    def test_attachment(self, smtp_cls):
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server
        with open("dummy.txt", "w") as f:
            f.write("data")
        try:
            client = self.make_client()
            client.send(to="a@example.com", subject="S", body="b", attachments=["dummy.txt"])
            msg = server.send_message.call_args[0][0]
            parts = [p.get_content_type() for p in msg.iter_parts()]
            self.assertIn("text/plain", parts)
        finally:
            import os
            os.remove("dummy.txt")

    @patch("gmail_client.smtplib.SMTP_SSL")
    def test_attachment_unknown_extension_falls_back(self, smtp_cls):
        server = MagicMock()
        smtp_cls.return_value.__enter__.return_value = server
        with open("data.xyzunk", "wb") as f:
            f.write(b"bytes")
        try:
            client = self.make_client()
            client.send(to="a@example.com", subject="S", body="b", attachments=["data.xyzunk"])
            msg = server.send_message.call_args[0][0]
            parts = [p.get_content_type() for p in msg.iter_parts()]
            self.assertIn("application/octet-stream", parts)
        finally:
            import os
            os.remove("data.xyzunk")

    def test_missing_credentials(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                GmailClient(address="", password="")


if __name__ == "__main__":
    unittest.main()
