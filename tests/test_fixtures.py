import json
from pathlib import Path
from app.core import evaluate_receiver
FIX=Path(__file__).parents[1]/"fixtures"

def test_strong_receiver_outscores_fragile_under_chaos():
    strong=json.loads((FIX/"receiver-strong.json").read_text())
    fragile=json.loads((FIX/"receiver-fragile.json").read_text())
    scenario=json.loads((FIX/"chaos-scenario.json").read_text())
    assert evaluate_receiver(strong,scenario)["resilience_score"] > evaluate_receiver(fragile,scenario)["resilience_score"]
