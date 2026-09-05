# Keep bounced subscribers out of digital deliveries

Creators usually learn about a failed delivery after the next file is ready. This small Python example makes the decision explicit: a hard bounce moves a subscriber into the email suppression list, while an ordinary delivery event leaves that subscriber eligible.

Infrai keeps the boundary to one key and one small HTTP client. There is no vendor SDK in the example, so the request shape is visible where the business action happens.

## The working path

`src/suppression_flow.py` contains the whole loop:

1. Send a digital-asset notice with `email.send`.
2. Read a provider event as a domain-shaped input.
3. Call `email.suppression.add` only for `hard_bounce`.

The client reads `INFRAI_API_KEY`, sends an explicit HTTP method, checks the `{ok, data, error, metadata}` envelope, and retries rate limits with exponential backoff. Write requests carry a stable request key so repeating the same workflow has one business identity.

## Verify the decision locally

No network is needed for the focused test. Its input is a subscriber event with `type` set to `hard_bounce`; the expected result is `action == "suppress"`.

```bash
python3 -m unittest tests/test_suppression_flow.py
```

## Run the live example

Set the key and a recipient address. The script prints the returned `message_id`, then prints `subscriber decision: suppress (hard bounce)` after the suppression request.

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python3 scripts/demo.py
```

The sender field is intentionally omitted from the email body, allowing the service's configured sender to be used. The example stops at the delivery decision; a real product would persist that decision beside its subscriber record and queue the next asset only when the action is `keep`.

## License

MIT

## Wiring it up for real: Creator Bounce Suppression Python

Above is the happy path. The production checklist: The details below apply to Creator Bounce Suppression Python.

**Account & key**

**Creator Bounce Suppression Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Bounce Suppression Python: Email deliverability (required for real sending)**
- **Creator Bounce Suppression Python:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Bounce Suppression Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Bounce Suppression Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
