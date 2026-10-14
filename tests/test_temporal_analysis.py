from src.temporal_analysis import detect_quiet_intervals

audio_path = r"C:\Users\CHANDRU\Downloads\example_fsc.wav"

try:
    intervals = detect_quiet_intervals(audio_path)
    print("\n===== TEMPORAL ANALYSIS =====")

    if intervals:
        for index, interval in enumerate(intervals, start=1):
            print(f"\nQuiet interval {index}")
            print(f"Start: {interval['start_seconds']} seconds")
            print(f"End: {interval['end_seconds']} seconds")
            print(f"Duration: {interval['duration_seconds']} seconds")
    else:
        print("No quiet intervals detected.")
except Exception as error:
    print(f"Analysis failed: {error}")
