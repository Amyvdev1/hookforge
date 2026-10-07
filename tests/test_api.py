from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_unbounded_and_wrong_type_simulations_are_rejected():
    for count in (-1, 1000000, 'many', True):
        assert client.post('/api/simulate',json={'scenario':{'duplicate_count':count}}).status_code==422
def test_simulate_endpoint():
    r=client.post('/api/simulate',json={'capabilities':{},'scenario':{'duplicate_count':2}})
    assert r.status_code==200 and 'evaluation' in r.json()
