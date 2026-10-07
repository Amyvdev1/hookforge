from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_simulate_endpoint():
    r=client.post('/api/simulate',json={'capabilities':{},'scenario':{'duplicate_count':2}})
    assert r.status_code==200 and 'evaluation' in r.json()
