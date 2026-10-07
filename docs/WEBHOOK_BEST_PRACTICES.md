# Webhook Reliability Checklist

- verify signatures against the exact raw body
- enforce replay/timestamp tolerance
- deduplicate by stable provider event ID
- make side effects idempotent
- acknowledge quickly and queue slow work
- preserve full event history while keeping summary state monotonic
- validate payloads before business logic
- tolerate unknown event types safely
- log request, message, and event correlation IDs
- document retry semantics for integrators
