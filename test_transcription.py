
from src.transcription import transcribe_audio

audio_path = r"C:\Users\CHANDRU\Downloads\example_fsc.wav"

segments = transcribe_audio(audio_path)

print("\nTRANSCRIPTION RESULTS\n")

for segment in segments:
    print(
        f"{segment['start']:.2f}s - "
        f"{segment['end']:.2f}s: "
        f"{segment['text']}"
    )
