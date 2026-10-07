from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from .core import CAPABILITIES, evaluate_receiver, simulate_delivery, sign_payload, verify_signature

BASE=Path(__file__).resolve().parent
app=FastAPI(title='HookForge',version='1.0.0',description='Webhook resilience workbench')
app.mount('/static',StaticFiles(directory=BASE/'static'),name='static')

class ScenarioInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    duplicate_count: int = Field(default=1, ge=1, le=100)
    delay_seconds: int = Field(default=0, ge=0, le=3600)
    out_of_order: bool = False
    valid_signature: bool = True
    retry_count: int = Field(default=0, ge=0, le=100)
    timeout_ms: int = Field(default=0, ge=0, le=60000)
    malformed_payload: bool = False
    unknown_event_type: bool = False

class Evaluation(BaseModel):
    capabilities: dict[str,bool] = Field(default_factory=dict)
    scenario: ScenarioInput = Field(default_factory=ScenarioInput)
class SignaturePayload(BaseModel):
    secret:str='demo-secret'; timestamp:int; payload:dict[str,Any]; signature:str|None=None

@app.get('/',include_in_schema=False)
def home(): return FileResponse(BASE/'static'/'index.html')
@app.get('/health')
def health(): return {'status':'ok','service':'hookforge','version':'1.0.0'}
@app.get('/api/capabilities')
def capabilities(): return {'capabilities':CAPABILITIES}
@app.post('/api/evaluate')
def evaluate(payload:Evaluation): return evaluate_receiver(payload.capabilities,payload.scenario.model_dump())
@app.post('/api/simulate')
def simulate(payload:Evaluation): return simulate_delivery(payload.capabilities,payload.scenario.model_dump())
@app.post('/api/sign')
def sign(p:SignaturePayload): return {'signature':sign_payload(p.secret,p.timestamp,p.payload)}
@app.post('/api/verify')
def verify(p:SignaturePayload): return {'valid':bool(p.signature) and verify_signature(p.secret,p.timestamp,p.payload,p.signature)}
