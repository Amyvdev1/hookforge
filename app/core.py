from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import hmac
import json
from typing import Any

CAPABILITIES = {
    "signature_verification": 18,
    "duplicate_protection": 17,
    "retry_safety": 15,
    "event_ordering": 12,
    "payload_validation": 10,
    "timeout_handling": 8,
    "actionable_errors": 8,
    "correlation_logging": 7,
    "unknown_event_handling": 5,
}

@dataclass(frozen=True)
class Scenario:
    duplicate_count: int = 1
    delay_seconds: int = 0
    out_of_order: bool = False
    valid_signature: bool = True
    retry_count: int = 0
    timeout_ms: int = 0
    malformed_payload: bool = False
    unknown_event_type: bool = False

    def to_dict(self) -> dict[str, Any]: return asdict(self)


def sign_payload(secret: str, timestamp: int, payload: dict[str, Any]) -> str:
    raw=json.dumps(payload,separators=(",",":"),sort_keys=True)
    message=f"{timestamp}.{raw}".encode()
    return hmac.new(secret.encode(),message,sha256).hexdigest()


def verify_signature(secret: str, timestamp: int, payload: dict[str, Any], signature: str) -> bool:
    return hmac.compare_digest(sign_payload(secret,timestamp,payload),signature)


def evaluate_receiver(capabilities: dict[str, bool], scenario: dict[str, Any] | None = None) -> dict[str, Any]:
    s=Scenario(**{k:v for k,v in (scenario or {}).items() if k in Scenario.__dataclass_fields__})
    checks=[]
    for name,weight in CAPABILITIES.items():
        passed=bool(capabilities.get(name,False))
        checks.append({"capability":name,"status":"pass" if passed else "fail","weight":weight,"why":_capability_reason(name)})
    score=sum(c["weight"] for c in checks if c["status"]=="pass")
    scenario_risks=_scenario_risks(s,capabilities)
    penalty=min(35,sum(r["penalty"] for r in scenario_risks))
    adjusted=max(0,score-penalty)
    grade="excellent" if adjusted>=90 else "strong" if adjusted>=75 else "fragile" if adjusted>=50 else "unsafe"
    return {
        "resilience_score":adjusted,
        "baseline_score":score,
        "scenario_penalty":penalty,
        "grade":grade,
        "checks":checks,
        "scenario":s.to_dict(),
        "scenario_risks":scenario_risks,
        "recommendations":_recommendations(checks,scenario_risks),
    }


def simulate_delivery(capabilities: dict[str, bool], scenario: dict[str, Any]) -> dict[str, Any]:
    s=Scenario(**{k:v for k,v in scenario.items() if k in Scenario.__dataclass_fields__})
    events=[]
    base=[{"id":"evt_001","type":"order.created","occurred_at":1000},{"id":"evt_002","type":"order.updated","occurred_at":1010}]
    if s.out_of_order: base=list(reversed(base))
    if s.unknown_event_type: base.append({"id":"evt_999","type":"unknown.experimental","occurred_at":1020})
    if s.malformed_payload: base.append({"id":None,"type":None,"occurred_at":"bad"})
    deliveries=[]
    for event in base:
        copies=max(1,s.duplicate_count if event.get("id")=="evt_001" else 1)
        for i in range(copies):
            deliveries.append({**event,"delivery_attempt":i+1,"delay_seconds":s.delay_seconds})
    if s.retry_count:
        for i in range(s.retry_count): deliveries.append({"id":"evt_retry","type":"order.updated","occurred_at":1030,"delivery_attempt":i+2,"delay_seconds":s.delay_seconds})
    seen=set(); state="pending"
    for d in deliveries:
        valid=bool(d.get("id") and d.get("type"))
        duplicate=d.get("id") in seen if d.get("id") else False
        accepted=True; notes=[]
        if not s.valid_signature and capabilities.get("signature_verification"):
            accepted=False; notes.append("rejected invalid signature")
        if not valid and capabilities.get("payload_validation"):
            accepted=False; notes.append("rejected malformed payload")
        if duplicate and capabilities.get("duplicate_protection"):
            accepted=False; notes.append("deduplicated")
        if d.get("type")=="unknown.experimental" and capabilities.get("unknown_event_handling"):
            notes.append("ignored unknown event safely")
        if accepted and d.get("id"): seen.add(d["id"])
        if accepted and d.get("type")=="order.created": state="created"
        if accepted and d.get("type")=="order.updated": state="updated"
        events.append({**d,"accepted":accepted,"duplicate":duplicate,"notes":notes})
    return {"final_state":state,"unique_event_ids":len(seen),"deliveries":events,"evaluation":evaluate_receiver(capabilities,scenario)}


def _scenario_risks(s: Scenario, caps: dict[str,bool]) -> list[dict[str,Any]]:
    risks=[]
    def add(code,msg,cap,penalty):
        if not caps.get(cap,False): risks.append({"code":code,"message":msg,"missing_capability":cap,"penalty":penalty})
    if not s.valid_signature: add("invalid-signature","Invalid signatures can mutate state if verification is absent.","signature_verification",12)
    if s.duplicate_count>1: add("duplicates",f"The same event may arrive {s.duplicate_count} times and be processed more than once.","duplicate_protection",10)
    if s.retry_count>0: add("retries",f"Provider retries ({s.retry_count}) can duplicate side effects without retry-safe handling.","retry_safety",8)
    if s.out_of_order: add("ordering","Events arrive out of lifecycle order and may regress summary state.","event_ordering",8)
    if s.malformed_payload: add("malformed","Malformed payloads can reach business logic without validation.","payload_validation",7)
    if s.timeout_ms>0: add("timeout",f"Receiver latency/timeout risk is simulated at {s.timeout_ms} ms.","timeout_handling",5)
    if s.unknown_event_type: add("unknown-event","New event types should not crash or corrupt the receiver.","unknown_event_handling",4)
    return risks


def _recommendations(checks,risks):
    out=[]
    for c in checks:
        if c["status"]=="fail": out.append(f"Implement {c['capability'].replace('_',' ')}: {c['why']}")
    for r in risks:
        out.append(f"Scenario risk: {r['message']}")
    return out[:10]


def _capability_reason(name:str)->str:
    return {
        "signature_verification":"Authenticate the sender before trusting payload content.",
        "duplicate_protection":"Use stable provider event IDs or idempotency keys.",
        "retry_safety":"Ensure repeated delivery cannot repeat external side effects.",
        "event_ordering":"Keep lifecycle summary state monotonic while preserving raw history.",
        "payload_validation":"Reject malformed or structurally invalid events before business logic.",
        "timeout_handling":"Acknowledge quickly and move slow work off the request path.",
        "actionable_errors":"Return intentional statuses and log the next debugging action.",
        "correlation_logging":"Log request/event IDs so support can trace one delivery end to end.",
        "unknown_event_handling":"Ignore or quarantine unknown event types safely.",
    }[name]
