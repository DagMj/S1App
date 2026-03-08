from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.generators.core.registry import registry
from app.generators.library import register_all_generators
from app.models.task import ProblemInstance


def test_exam_mode_generates_10_tasks(client, auth_headers):
    response = client.post('/api/v1/modes/exam/start', headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['mode'] == 'exam'
    assert len(payload['items']) == 10

    del1 = [item for item in payload['items'] if item['part'] == 'del1']
    del2 = [item for item in payload['items'] if item['part'] == 'del2']
    assert len(del1) == 6
    assert len(del2) == 4


def test_exam_mode_prioritizes_non_trivial_difficulty(client, auth_headers):
    register_all_generators()

    response = client.post('/api/v1/modes/exam/start', headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()

    for item in payload['items']:
        difficulty = registry.get(item['generator_key']).metadata().difficulty
        assert difficulty >= 2


def test_training_flow_submit_answer(client, auth_headers):
    start = client.post(
        '/api/v1/modes/training/start',
        headers=auth_headers,
        json={'mode': 'training_single', 'generator_keys': ['linear_equation']},
    )
    assert start.status_code == 200, start.text
    session_id = start.json()['session_id']

    nxt = client.post(f'/api/v1/modes/training/{session_id}/next', headers=auth_headers)
    assert nxt.status_code == 200, nxt.text
    next_payload = nxt.json()
    session_item_id = next_payload['session_item_id']

    db: Session = SessionLocal()
    try:
        problem = db.query(ProblemInstance).filter(ProblemInstance.session_item_id == session_item_id).first()
        assert problem is not None
        answer = str(problem.correct_answer)
    finally:
        db.close()

    submit = client.post(
        f'/api/v1/modes/sessions/{session_id}/submit',
        headers=auth_headers,
        json={'session_item_id': session_item_id, 'answer': answer},
    )
    assert submit.status_code == 200, submit.text
    payload = submit.json()
    assert payload['is_correct'] is True

    summary = client.get(f'/api/v1/modes/sessions/{session_id}/summary', headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json()['solved'] >= 1

def test_exam_mode_rejects_resubmission_of_same_item(client, auth_headers):
    start = client.post('/api/v1/modes/exam/start', headers=auth_headers)
    assert start.status_code == 200, start.text
    payload = start.json()

    first_item = payload['items'][0]
    session_id = payload['session_id']
    session_item_id = first_item['session_item_id']

    db: Session = SessionLocal()
    try:
        problem = db.query(ProblemInstance).filter(ProblemInstance.session_item_id == session_item_id).first()
        assert problem is not None
        answer = str(problem.correct_answer)
    finally:
        db.close()

    first_submit = client.post(
        f'/api/v1/modes/sessions/{session_id}/submit',
        headers=auth_headers,
        json={'session_item_id': session_item_id, 'answer': answer},
    )
    assert first_submit.status_code == 200, first_submit.text

    second_submit = client.post(
        f'/api/v1/modes/sessions/{session_id}/submit',
        headers=auth_headers,
        json={'session_item_id': session_item_id, 'answer': answer},
    )
    assert second_submit.status_code == 400
