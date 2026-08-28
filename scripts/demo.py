import os
import sys
from pathlib import Path

# Make the documented direct entry point work from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.suppression_flow import InfraiClient, process_bounce, send_digital_asset


def main() -> None:
    client = InfraiClient()
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("set DEMO_EMAIL_TO before running the live example")
    message_id = send_digital_asset(client, recipient, "Creator field notes", "https://example.com/download")
    print(f"sent message {message_id}")
    decision = process_bounce(client, {"subscriber": recipient, "type": "hard_bounce"})
    print(f"subscriber decision: {decision.action} ({decision.reason})")


if __name__ == "__main__":
    main()
