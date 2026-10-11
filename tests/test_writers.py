import json

from vid2text.engine import Segment, Transcript
from vid2text.writers import write_json, write_txt

SAMPLE = Transcript("ru", 125.4, [Segment(0, 3, " Привет, мир. "), Segment(61, 65, "Пока.")])


def test_txt_plain(tmp_path):
    out = tmp_path / "a.txt"
    write_txt(SAMPLE, out)
    assert out.read_text(encoding="utf-8") == "Привет, мир.\nПока.\n"


def test_txt_with_timestamps(tmp_path):
    out = tmp_path / "a.txt"
    write_txt(SAMPLE, out, timestamps=True)
    assert out.read_text(encoding="utf-8").splitlines() == [
        "[00:00:00] Привет, мир.",
        "[00:01:01] Пока.",
    ]


def test_json_structure_keeps_unicode(tmp_path):
    out = tmp_path / "a.json"
    write_json(SAMPLE, out, tmp_path / "video.mp4")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["source"] == "video.mp4"
    assert data["language"] == "ru"
    assert data["duration"] == 125.4
    assert data["text"] == "Привет, мир. Пока."
    assert data["segments"][1] == {"start": 61, "end": 65, "text": "Пока."}
    assert "Привет" in out.read_text(encoding="utf-8")
