import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pop_client.pop_reader import PopClient


def main():
    parser = argparse.ArgumentParser(description="Read mail via Gmail POP3")
    parser.add_argument("--list", action="store_true", help="List latest messages")
    parser.add_argument("--limit", type=int, default=10, help="How many messages (default 10)")
    parser.add_argument("--read", type=int, metavar="NUM", help="Read a specific message number")
    parser.add_argument("--latest", type=int, metavar="N", help="Read the N most recent messages")
    parser.add_argument("--attachments", metavar="DIR", help="Save attachments of --read message to DIR")
    parser.add_argument("--recent", action="store_true", help="Use POP 'recent mode' (fetch all mail, bypass windowed mode)")
    args = parser.parse_args()

    try:
        with PopClient(recent=args.recent) as client:
            if args.read:
                msg = client.fetch(args.read, save_dir=args.attachments)
                print(f"From:    {client._decode(msg['From'])}")
                print(f"Subject: {client._decode(msg['Subject'])}")
                print(f"Date:    {client._decode(msg['Date'])}")
                print("-" * 50)
                print(client.get_body(msg))
            elif args.latest:
                for msg in client.fetch_latest(args.latest):
                    print(f"[{client._decode(msg['Date'])}] {client._decode(msg['From'])}")
                    print(f"  {client._decode(msg['Subject'])}")
                    print("-" * 50)
            else:
                for item in client.list_messages(args.limit):
                    print(f"#{item['num']:<4} {item['date']}")
                    print(f"     From: {item['from']}")
                    print(f"     Subj: {item['subject']}")
                    print("-" * 50)
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
