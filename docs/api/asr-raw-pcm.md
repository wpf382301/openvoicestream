# Raw PCM uploads for ASR

The non-streaming `POST /asr` endpoint accepts the usual WAV/FLAC containers
and also accepts an explicitly labeled raw PCM upload. Raw uploads are
interpreted as signed 16-bit little-endian PCM, mono, 16 kHz. The bytes are
wrapped in a WAV container in memory before the selected ASR backend runs.

```bash
curl -X POST 'http://device:8621/asr?language=auto' \
  -H 'Accept: application/json' \
  -F 'file=@capture.raw;filename=capture.raw;type=audio/raw'
```

The raw format is selected when the media type is `audio/raw`, `audio/pcm`,
`audio/L16`, `audio/x-pcm`, or `audio/x-raw`, or when the filename ends in
`.raw` or `.pcm`. A generic `application/octet-stream` upload is left
unchanged so malformed container requests still produce the backend's normal
error. An empty or odd-length raw payload receives HTTP 400.

For low-latency incremental results, use the WebSocket `/asr/stream` protocol;
it accepts the same PCM16 format as binary frames and uses an empty binary
frame to finalize an utterance.
