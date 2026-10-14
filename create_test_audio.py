
from pathlib import Path
import librosa
import soundfile as sf

# Original sample audio
input_path = Path(r"C:\Users\CHANDRU\Downloads\example_fsc.wav")

# Output folder for test recordings
output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

# Load original audio
audio, sample_rate = librosa.load(
    str(input_path),
    sr=None,
    mono=True
)

# Create a slower version for controlled testing
slower_audio = librosa.effects.time_stretch(
    audio,
    rate=0.85
)

# Save the new recording
output_path = output_folder / "example_fsc_slower.wav"

sf.write(
    str(output_path),
    slower_audio,
    sample_rate
)

print("Original audio:", input_path)
print("Modified audio:", output_path.resolve())
print("Original duration:", round(len(audio) / sample_rate, 2), "seconds")
print("Modified duration:", round(len(slower_audio) / sample_rate, 2), "seconds")
