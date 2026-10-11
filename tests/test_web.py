import pytest
from fastapi.testclient import TestClient

from vid2text.web.app import create_app


@pytest.fixture
def client(fake_engine):
    app = create_app(engine_factory=lambda model: fake_engine)
    return TestClient(app)


def payload(tmp_path, **kw):
    base = {"input_dir": str(tmp_path / "in"), "output_dir": str(tmp_path / "out")}
    return {**base, **kw}


def test_index_and_config(client):
    assert "vid2text" in client.get("/").text
    cfg = client.get("/api/config").json()
    assert "base" in cfg["models"] and ".mp4" in cfg["extensions"]


def test_browse_lists_folders_and_counts_media(client, tmp_path):
    (tmp_path / "videos").mkdir()
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "clip.mp4").write_bytes(b"x")
    data = client.get("/api/browse", params={"path": str(tmp_path)}).json()
    assert [d["name"] for d in data["dirs"]] == ["videos"]
    assert data["media_files"] == 1


def test_browse_unknown_folder_404(client, tmp_path):
    assert client.get("/api/browse", params={"path": str(tmp_path / "nope")}).status_code == 404


def test_roots_restrict_browsing(fake_engine, tmp_path, monkeypatch):
    monkeypatch.setenv("VID2TEXT_ROOTS", str(tmp_path / "data"))
    (tmp_path / "data").mkdir()
    client = TestClient(create_app(engine_factory=lambda m: fake_engine))
    assert client.get("/api/browse", params={"path": str(tmp_path)}).status_code == 403
    inside = client.get("/api/browse", params={"path": str(tmp_path / "data")}).json()
    assert inside["parent"] is None


def test_full_job_through_api(client, tmp_path, clip_factory):
    clip_factory("demo.mp4")
    res = client.post("/api/jobs", json=payload(tmp_path, formats=["txt"]))
    assert res.status_code == 202
    client.app.state.jobs.wait(30)

    state = client.get("/api/jobs/current").json()
    assert state["status"] == "finished"
    assert state["results"][0]["status"] == "done"
    assert (tmp_path / "out" / "demo.txt").exists()


def test_job_validation_errors(client, tmp_path):
    assert client.post("/api/jobs", json=payload(tmp_path)).status_code == 400  # input missing
    assert client.post("/api/jobs", json=payload(tmp_path, model="huge")).status_code == 400
    assert client.post("/api/jobs", json={"input_dir": "", "output_dir": ""}).status_code == 400
