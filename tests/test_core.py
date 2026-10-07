from app.core import CAPABILITIES,evaluate_receiver,sign_payload,verify_signature,simulate_delivery

def full_caps(): return {k:True for k in CAPABILITIES}

def test_ordering_guard_prevents_state_regression():
    safe=simulate_delivery(full_caps(),{'out_of_order':True})
    assert safe['final_state']=='updated'
    assert safe['deliveries'][1]['accepted'] is False
    assert 'stale' in safe['deliveries'][1]['notes'][0]
    assert simulate_delivery({}, {'out_of_order':True})['final_state']=='created'

def test_unknown_events_are_ignored_when_protected():
    result=simulate_delivery(full_caps(),{'unknown_event_type':True})
    assert result['deliveries'][-1]['accepted'] is False
    assert result['unique_event_ids']==2

def test_full_receiver_scores_100_on_benign_scenario(): assert evaluate_receiver(full_caps(),{})['resilience_score']==100

def test_duplicate_risk_is_explained():
    result=evaluate_receiver({}, {'duplicate_count':3})
    assert any('more than once' in x['message'] for x in result['scenario_risks'])

def test_signature_round_trip():
    p={'id':'evt_1'}; sig=sign_payload('s',100,p)
    assert verify_signature('s',100,p,sig)
    assert not verify_signature('bad',100,p,sig)

def test_resilient_simulation_deduplicates_and_rejects_invalid():
    d=simulate_delivery(full_caps(),{'duplicate_count':3,'valid_signature':False})
    assert all(not row['accepted'] for row in d['deliveries'])

def test_fragile_receiver_gets_scenario_penalty():
    d=evaluate_receiver({}, {'duplicate_count':3,'retry_count':2,'out_of_order':True})
    assert d['scenario_penalty']>0 and d['resilience_score']==0
