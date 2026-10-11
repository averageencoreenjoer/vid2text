import wave

import numpy as np

from vid2text.engine import Segment, Transcript, _read_wav


def test_read_wav_scales_samples_to_unit_range(tmp_path):
    path = tmp_path / "a.wav"
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(16000)
        out.writeframes(np.array([0, 16384, -32768], dtype=np.int16).tobytes())

    samples = _read_wav(path)

    assert samples.dtype == np.float32
    assert samples.tolist() == [0.0, 0.5, -1.0]


def test_transcript_text_joins_non_empty_segments():
    t = Transcript("en", 3, [Segment(0, 1, " Hi "), Segment(1, 2, ""), Segment(2, 3, "there")])
    assert t.text == "Hi there"
