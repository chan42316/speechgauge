import librosa
import numpy as np
from pathlib import Path


def detect_quiet_intervals(
    audio_path,
    threshold_ratio=0.08,
    min_pause_seconds=0.25
):
    """Detect approximate low-energy intervals and their timestamps."""

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    audio, sample_rate = librosa.load(
        str(audio_path),
        sr=22050,
        mono=True
    )

    if len(audio) == 0:
        raise ValueError("The audio file is empty.")

    frame_length = 2048
    hop_length = 512

    rms = librosa.feature.rms(
        y=audio,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]

    threshold = max(float(np.max(rms)) * threshold_ratio, 1e-5)
    quiet_frames = rms <= threshold

    frame_step = hop_length / sample_rate
    min_frames = max(
        1,
        int(np.ceil(min_pause_seconds / frame_step))
    )

    intervals = []
    start_frame = None

    for i, is_quiet in enumerate(quiet_frames):
        if is_quiet and start_frame is None:
            start_frame = i

        elif not is_quiet and start_frame is not None:
            end_frame = i

            if end_frame - start_frame >= min_frames:
                start_time = start_frame * frame_step
                end_time = min(
                    end_frame * frame_step,
                    len(audio) / sample_rate
                )

                intervals.append({
                    "start_seconds": round(start_time, 2),
                    "end_seconds": round(end_time, 2),
                    "duration_seconds": round(
                        end_time - start_time, 2
                    )
                })

            start_frame = None

    if start_frame is not None:
        end_time = len(audio) / sample_rate

        if len(quiet_frames) - start_frame >= min_frames:
            start_time = start_frame * frame_step

            intervals.append({
                "start_seconds": round(start_time, 2),
                "end_seconds": round(end_time, 2),
                "duration_seconds": round(
                    end_time - start_time, 2
                )
            })

    return intervals
