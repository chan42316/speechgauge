from src.audio_features import extract_audio_features

audio_path = input("Enter the path to a speech audio file: ").strip().strip('"')

try:
    results = extract_audio_features(audio_path)
    for name, value in results.items():
        print(f"{name}: {value}")
except Exception as error:
    print(f"Analysis failed: {error}")