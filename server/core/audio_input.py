"""Normalize uploaded audio containers for the non-streaming ASR API."""

from __future__ import annotations

import io
import wave


_RAW_CONTENT_TYPES = frozenset(
    {
        "audio/l16",
        "audio/pcm",
        "audio/raw",
        "audio/x-pcm",
        "audio/x-raw",
    }
)
_RAW_SUFFIXES = (".pcm", ".raw")


def is_raw_pcm_upload(*, content_type: str | None, filename: str | None) -> bool:
    """Return whether an upload is explicitly labeled as PCM data.

    Generic ``application/octet-stream`` is intentionally excluded: treating
    arbitrary binary uploads as audio would hide malformed requests.
    """

    media_type = (content_type or "").split(";", 1)[0].strip().lower()
    name = (filename or "").strip().lower()
    return media_type in _RAW_CONTENT_TYPES or name.endswith(_RAW_SUFFIXES)


def normalize_uploaded_audio(
    audio_bytes: bytes,
    *,
    content_type: str | None = None,
    filename: str | None = None,
    sample_rate: int = 16000,
    channels: int = 1,
) -> bytes:
    """Wrap explicitly labeled PCM16 little-endian audio in a WAV container.

    The bridge protocol sends 16 kHz, mono, signed PCM16 little-endian bytes
    as ``audio/raw``.  The backend accepts WAV/FLAC containers, so wrapping is
    done in memory and no temporary audio file is created.  Other containers
    are returned byte-for-byte unchanged.
    """

    if not is_raw_pcm_upload(content_type=content_type, filename=filename):
        return audio_bytes
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    if channels <= 0:
        raise ValueError("channels must be positive")
    frame_width = 2 * channels
    if len(audio_bytes) == 0:
        raise ValueError("raw PCM upload is empty")
    if len(audio_bytes) % frame_width:
        raise ValueError(
            f"raw PCM upload length must be a multiple of {frame_width} bytes"
        )

    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_bytes)
    return output.getvalue()
