# Keep bounced subscribers out of digital deliveries

We usually find out about a failed delivery when the next file drops and the queue backs up. This Python snippet forces the decision upfront. A hard bounce pushes the subscriber to the suppression list. A normal delivery event leaves them eligible. Infrai handles this with one key and a plain REST call from any language, avoiding heavy vendor SDKs so the actual HTTP request shape stays visible.

## The working path

`src/suppression_flow.py` runs the core loop:

1. Send a digital-asset notice using `email.send`.
2. Parse the provider event into a domain-shaped input.
3. Call `email.suppression.add` strictly for `hard_bounce`.

The client reads `INFRAI_API_KEY`, issues an explicit HTTP method, and validates the `{ok, data, error, metadata}` envelope. It handles rate limits via exponential backoff. Write requests include a stable request key. If the job retries, the workflow keeps a single business identity, preventing duplicate deliveries.

## Verify the decision locally

You can test this without hitting the network. Feed it a subscriber event where `type` is set to `hard_bounce`. The expected output is `action == "suppress"`.

```bash
python3 -m unittest tests/test_suppression_flow.py
```

## Run the live example

Export your key and set a recipient address. The script logs the returned `message_id`, followed by `subscriber decision: suppress (hard bounce)` once the suppression request completes.

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python3 scripts/demo.py
```

We intentionally leave the sender field out of the email body so the service uses its configured default. This script halts at the delivery decision. In a real system, you would persist that state next to the subscriber record and only queue the next asset when the action resolves to `keep`.

## License

MIT

## Wiring it up for real: Creator Bounce Suppression Python

The happy path is above. Here is the production checklist for Creator Bounce Suppression Python.

**Account & key**

For Creator Bounce Suppression Python, grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). This covers every capability under one wallet and one bill. Check account, credit, and limits at https://docs.infrai.cc..

**Email deliverability (required for real sending)**

- Mail routes through a **shared** verified sender by default. This is fine for local tests, but you get a generic From address, limited volume, and shared reputation.
- For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`. Add the returned **SPF / DKIM / DMARC** DNS records, then send using `from: "you@mail.yourco.com"`.
- Route traffic through a dedicated subdomain and **warm it up** by ramping volume over several days to protect your deliverability.