
import librosa
import numpy as np
from pathlib import Path


def align_speech_audio(reference_path, participant_path):
    """
    Align reference and participant audio using MFCC features
    and Dynamic Time Warping (DTW).

    Returns approximate acoustic alignment information.
    """

    reference_path = Path(reference_path)
    participant_path = Path(participant_path)

    if not reference_path.exists():
        raise FileNotFoundError(
            f"Reference audio not found: {reference_path}"
        )

    if not participant_path.exists():
        raise FileNotFoundError(
            f"Participant audio not found: {participant_path}"
        )

    # Load both recordings at the same sample rate.
    reference_audio, sr = librosa.load(
        str(reference_path),
        sr=22050,
        mono=True
    )

    participant_audio, _ = librosa.load(
        str(participant_path),
        sr=22050,
        mono=True
    )

    if len(reference_audio) == 0:
        raise ValueError("Reference audio is empty.")

    if len(participant_audio) == 0:
        raise ValueError("Participant audio is empty.")

    # Extract 13 MFCC coefficients from each recording.
    reference_mfcc = librosa.feature.mfcc(
        y=reference_audio,
        sr=sr,
        n_mfcc=13,
        hop_length=512
    )

    participant_mfcc = librosa.feature.mfcc(
        y=participant_audio,
        sr=sr,
        n_mfcc=13,
        hop_length=512
    )

    # Normalize MFCC features across time.
    reference_mean = np.mean(
        reference_mfcc, axis=1, keepdims=True
    )
    reference_std = np.std(
        reference_mfcc, axis=1, keepdims=True
    )

    reference_mfcc = (
        reference_mfcc - reference_mean
    ) / np.maximum(reference_std, 1e-6)

    participant_mean = np.mean(
        participant_mfcc, axis=1, keepdims=True
    )
    participant_std = np.std(
        participant_mfcc, axis=1, keepdims=True
    )

    participant_mfcc = (
        participant_mfcc - participant_mean
    ) / np.maximum(participant_std, 1e-6)

    # Align the feature sequences using Dynamic Time Warping.
    cost, path = librosa.sequence.dtw(
        X=reference_mfcc,
        Y=participant_mfcc,
        metric="euclidean"
    )

    # Reverse the path into chronological order.
    path = path[::-1]

    hop_seconds = 512 / sr
    aligned_points = []

    for reference_frame, participant_frame in path:
        aligned_points.append({
            "reference_time": round(
                float(reference_frame * hop_seconds), 2
            ),
            "participant_time": round(
                float(participant_frame * hop_seconds), 2
            )
        })

    # Calculate normalized cumulative alignment cost.
    alignment_cost = float(cost[-1, -1]) / len(path)

    return {
        "reference_duration": round(
            len(reference_audio) / sr, 2
        ),
        "participant_duration": round(
            len(participant_audio) / sr, 2
        ),
        "alignment_cost": round(alignment_cost, 4),
        "aligned_points": aligned_points,
        "alignment_method": "MFCC + Dynamic Time Warping"
    }
