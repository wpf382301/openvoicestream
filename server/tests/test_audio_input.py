from __future__ import annotations

import io
import wave

import pytest

from server.core.audio_input import normalize_uploaded_audio


def test_raw_pcm_is_wrapped_as_wav_in_memory() -> None:
    pcm = b"\x01\x00\xff\x7f\x00\x80\x02\x00"
    wav_bytes = normalize_uploaded_audio(
        pcm,
        content_type="audio/raw; rate=16000",
        filename="capture.raw",
    )

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 16000
        assert wav.readframes(wav.getnframes()) == pcm


def test_container_upload_is_not_modified() -> None:
    original = b"RIFF\x00\x00\x00\x00WAVE"
    assert normalize_uploaded_audio(original, content_type="audio/wav") == original


def test_odd_raw_pcm_payload_is_rejected() -> None:
    with pytest.raises(ValueError, match="multiple of 2"):
        normalize_uploaded_audio(b"\x00", content_type="audio/raw")
