from faster_whisper import WhisperModel


def transcribe_audio(audio_path):
    """
    Transcribe speech and return approximate word-level timestamps.
    """
    model = WhisperModel("base", device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        vad_filter=True,
        word_timestamps=True
    )

    results = []

    for segment in segments:
        if segment.words:
            for word in segment.words:
                results.append({
                    "start": round(word.start, 2),
                    "end": round(word.end, 2),
                    "text": word.word.strip()
                })
        else:
            results.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            })

    return results