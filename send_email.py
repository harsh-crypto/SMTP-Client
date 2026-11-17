import argparse
import sys
from gmail_client import GmailClient


def main():
    parser = argparse.ArgumentParser(description="Send email via Gmail SMTP")
    parser.add_argument("--to", required=True, help="Recipient(s), comma-separated")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", help="Message body (or use --body-file)")
    parser.add_argument("--body-file", help="Read body from a file ('-' for stdin)")
    parser.add_argument("--cc", help="CC recipient(s)")
    parser.add_argument("--bcc", help="BCC recipient(s)")
    parser.add_argument("--attach", action="append", default=[], help="File path (repeatable)")
    parser.add_argument("--html", action="store_true", help="Send body as HTML")
    args = parser.parse_args()

    body = args.body
    if args.body_file:
        if args.body_file == "-":
            body = sys.stdin.read()
        else:
            with open(args.body_file, "r", encoding="utf-8") as f:
                body = f.read()
    if body is None:
        parser.error("Provide --body or --body-file")

    try:
        client = GmailClient()
        client.send(
            to=args.to,
            subject=args.subject,
            body=body,
            cc=args.cc,
            bcc=args.bcc,
            attachments=args.attach or None,
            html=args.html,
        )
        print(f"Sent '{args.subject}' to {args.to}")
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
