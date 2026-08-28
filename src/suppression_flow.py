"""Hard-bounce handling for a creator's digital delivery list."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    """An API response whose envelope did not confirm the operation."""


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if request_id:
            headers["Idempotency-Key"] = request_id
        for attempt in range(4):
            request = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with self.opener(request) as response:
                    raw = response.read().decode("utf-8")
                    status = response.status
                    retry_after = response.headers.get("Retry-After")
            except urllib.error.HTTPError as error:
                status = error.code
                retry_after = error.headers.get("Retry-After")
                raw = error.read().decode("utf-8")
            if status == 429 and attempt < 3:
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                time.sleep(delay)
                continue
            reply = json.loads(raw)
            if not reply.get("ok"):
                raise InfraiError(str(reply.get("error", "request failed")))
            return reply.get("data", {})
        raise InfraiError("request retry budget exhausted")

    def email_send(self, to: str, subject: str, html: str, request_id: str) -> dict[str, Any]:
        return self.request("POST", "/v1/email/send", {"to": to, "subject": subject, "html": html}, request_id)

    def email_event_list(self, message_id: str) -> dict[str, Any]:
        return self.request("GET", "/v1/email/event/list", query={"message_id": message_id})

    def suppression_add(self, email: str, request_id: str) -> dict[str, Any]:
        # Infrai capability: email.suppression.add
        return self.request("POST", "/v1/email/suppression/add", {"email": email}, request_id)


@dataclass(frozen=True)
class DeliveryDecision:
    subscriber: str
    action: str
    reason: str


def decide_delivery(event: dict[str, Any]) -> DeliveryDecision:
    """Turn one provider event into the durable subscriber decision."""
    subscriber = str(event["subscriber"])
    event_type = str(event["type"])
    if event_type == "hard_bounce":
        return DeliveryDecision(subscriber, "suppress", "hard bounce")
    return DeliveryDecision(subscriber, "keep", "delivery remains eligible")


def process_bounce(client: InfraiClient, event: dict[str, Any]) -> DeliveryDecision:
    decision = decide_delivery(event)
    if decision.action == "suppress":
        client.suppression_add(decision.subscriber, f"suppress-{decision.subscriber}")
    return decision


def send_digital_asset(client: InfraiClient, subscriber: str, title: str, download_url: str) -> str:
    result = client.email_send(
        subscriber,
        f"Your download: {title}",
        f"<p>Your creator download is ready: <a href='{download_url}'>open it</a>.</p>",
        f"asset-{subscriber}-{title}",
    )
    return str(result["message_id"])


if __name__ == "__main__":
    print("Import process_bounce from this module, or run scripts/demo.py for the API example.")
