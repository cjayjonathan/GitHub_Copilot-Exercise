from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should be a dict with known activity keys
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure email not present to start (remove if already there)
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up should succeed
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]

    # Signing up again should return 400
    resp2 = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp2.status_code == 400
    body2 = resp2.json()
    assert "already" in body2.get("detail", "").lower()

    # Cleanup: remove the participant
    del_resp = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert del_resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_delete_nonexistent_participant():
    activity = "Programming Class"
    email = "doesnotexist@example.com"

    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})
    assert resp.status_code == 404
    body = resp.json()
    assert "not found" in body.get("detail", "").lower()
