import uuid

from conftest import register_and_login


def _project(client, headers, name="Website"):
    r = client.post("/projects/", json={"name": name}, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_projects_are_scoped_to_owner(client):
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    pid = _project(client, alice)

    assert [p["id"] for p in client.get("/projects/", headers=alice).json()] == [pid]
    assert client.get("/projects/", headers=bob).json() == []
    assert client.get(f"/projects/{pid}", headers=bob).status_code == 404


def test_task_gets_priority_from_classifier(client):
    alice = register_and_login(client, "alice")
    pid = _project(client, alice)
    r = client.post(f"/tasks/{pid}/tasks", json={"title": "Prod crash", "description": "all users locked out"}, headers=alice)
    assert r.status_code == 200
    assert r.json()["priority"] == "critical"
    assert r.json()["ai_assigned_priority"] is True


def test_list_and_complete_task(client):
    alice = register_and_login(client, "alice")
    pid = _project(client, alice)
    tid = client.post(f"/tasks/{pid}/tasks", json={"title": "Fix login bug"}, headers=alice).json()["id"]

    r = client.patch(f"/tasks/{pid}/tasks/{tid}", json={"completed": True}, headers=alice)
    assert r.status_code == 200
    tasks = client.get(f"/tasks/{pid}/tasks", headers=alice).json()
    assert len(tasks) == 1 and tasks[0]["completed"] is True and tasks[0]["priority"] == "high"


def test_other_user_cannot_create_or_list_tasks(client):
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    pid = _project(client, alice)

    assert client.post(f"/tasks/{pid}/tasks", json={"title": "x"}, headers=bob).status_code == 404
    assert client.get(f"/tasks/{pid}/tasks", headers=bob).status_code == 404


def test_other_user_cannot_update_task(client):
    """Regression test: PATCH used to skip the project-ownership check."""
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")
    pid = _project(client, alice)
    tid = client.post(f"/tasks/{pid}/tasks", json={"title": "Original"}, headers=alice).json()["id"]

    r = client.patch(f"/tasks/{pid}/tasks/{tid}", json={"title": "Hijacked"}, headers=bob)
    assert r.status_code == 404
    assert client.get(f"/tasks/{pid}/tasks", headers=alice).json()[0]["title"] == "Original"


def test_task_in_wrong_project_not_found(client):
    alice = register_and_login(client, "alice")
    p1, p2 = _project(client, alice, "One"), _project(client, alice, "Two")
    tid = client.post(f"/tasks/{p1}/tasks", json={"title": "t"}, headers=alice).json()["id"]
    assert client.patch(f"/tasks/{p2}/tasks/{tid}", json={"completed": True}, headers=alice).status_code == 404


def test_malformed_ids_return_404(client):
    alice = register_and_login(client, "alice")
    pid = _project(client, alice)
    assert client.get("/projects/not-a-uuid", headers=alice).status_code == 404
    assert client.patch(f"/tasks/{pid}/tasks/not-a-uuid", json={}, headers=alice).status_code == 404
    assert client.get(f"/tasks/{uuid.uuid4()}/tasks", headers=alice).status_code == 404


def test_endpoints_require_auth(client):
    assert client.get("/projects/").status_code == 401
    assert client.post("/projects/", json={"name": "x"}).status_code == 401
