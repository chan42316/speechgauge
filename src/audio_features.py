
import librosa
import numpy as np
from pathlib import Path


def extract_audio_features(audio_path):
    """
    Extract measurable acoustic features from a speech recording.
    Returns real measurements calculated from the supplied audio.
    """

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load audio and convert it to mono at 22050 Hz.
    y, sr = librosa.load(str(audio_path), sr=22050, mono=True)

    if len(y) == 0:
        raise ValueError("The audio file is empty.")

    duration = len(y) / sr

    # Calculate RMS energy for short audio frames.
    rms = librosa.feature.rms(
        y=y,
        frame_length=2048,
        hop_length=512
    )[0]

    # Estimate which frames contain speech-like sound.
    # This is an energy-based approximation, not perfect speech recognition.
    threshold = max(float(np.max(rms)) * 0.08, 1e-5)
    active_frames = rms > threshold

    frame_times = librosa.frames_to_time(
        np.arange(len(rms)),
        sr=sr,
        hop_length=512
    )

    # Approximate pauses from consecutive inactive frames.
    frame_step = 512 / sr
    pause_durations = []
    inactive_count = 0

    for active in active_frames:
        if not active:
            inactive_count += 1
        else:
            pause_duration = inactive_count * frame_step

            if pause_duration >= 0.25:
                pause_durations.append(round(pause_duration, 2))

            inactive_count = 0

    # Include a final pause if the recording ends in silence.
    final_pause = inactive_count * frame_step
    if final_pause >= 0.25:
        pause_durations.append(round(final_pause, 2))

    # Estimate fundamental frequency (pitch).
    f0 = librosa.yin(
        y,
        fmin=65,
        fmax=400,
        sr=sr
    )

    valid_pitch = f0[np.isfinite(f0) & (f0 >= 65) & (f0 <= 400)]

    if len(valid_pitch) > 0:
        mean_pitch = float(np.mean(valid_pitch))
        pitch_std = float(np.std(valid_pitch))
    else:
        mean_pitch = None
        pitch_std = None

    # Extract Mel-frequency cepstral coefficients (MFCCs).
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=13
    )

    return {
        "file_name": audio_path.name,
        "duration_seconds": round(duration, 2),
        "estimated_active_audio_seconds": round(
            float(np.sum(active_frames) * frame_step), 2
        ),
        "pause_count": len(pause_durations),
        "pause_durations_seconds": pause_durations,
        "mean_pitch_hz": (
            round(mean_pitch, 2) if mean_pitch is not None else None
        ),
        "pitch_variation_hz": (
            round(pitch_std, 2) if pitch_std is not None else None
        ),
        "mfcc_mean": np.mean(mfcc, axis=1).round(3).tolist(),
        "mfcc_std": np.std(mfcc, axis=1).round(3).tolist(),
        "sample_rate": sr
    }
