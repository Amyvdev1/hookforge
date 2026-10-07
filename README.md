# HookForge

**Webhook Resilience Workbench.** HookForge stress-tests a receiver against the failure modes that make event-driven integrations difficult: invalid signatures, duplicate delivery, retries, out-of-order events, malformed payloads, timeouts, and unknown event types.

## Included in v1
- nine explicit receiver capabilities with weighted reliability scoring
- deterministic failure-scenario builder
- scenario-specific score penalties
- event delivery replay showing accepted/rejected/deduplicated events
- HMAC-SHA256 signing + constant-time verification helper
- duplicate, retry, ordering, payload, timeout, correlation, error, and unknown-event checks
- actionable recommendations
- polished browser workbench, FastAPI endpoints, tests, Docker, read-only CI

## Quick start
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Why it matters
Webhook reliability is not proven by returning HTTP 200 once. A receiver has to remain correct when providers retry, duplicate, delay, reorder, or evolve events.

## Interview story
> “MailTrace shows webhook behavior. HookForge goes one step further: it deliberately creates the failure modes and evaluates whether a receiver is resilient enough to survive them.”

## Evidence boundary
HookForge is a local simulator. It does not scan, probe, or attack external webhook endpoints. A production product would add sandbox callback targets with explicit ownership verification, worker queues, persisted replay sessions, latency measurements, and CI integration.

## CI setup status
The automated GitHub Actions workflow is pending upload authorization. The tests are included and can be run locally with python -m pytest. No passing GitHub CI run is claimed.

