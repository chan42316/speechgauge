
from src.temporal_analysis import detect_quiet_intervals
from src.temporal_comparison import compare_quiet_intervals

reference_path = r"C:\Users\CHANDRU\Downloads\example_fsc.wav"
participant_path = r"data\example_fsc_slower.wav"

reference_intervals = detect_quiet_intervals(reference_path)
participant_intervals = detect_quiet_intervals(participant_path)

comparisons = compare_quiet_intervals(
    reference_intervals,
    participant_intervals
)

print("\n===== SPEECHGAUGE TIMING DIFFERENCES =====")

if not comparisons:
    print("No corresponding quiet intervals available for comparison.")

for item in comparisons:
    print(f"\nQuiet interval {item['interval_number']}")
    print(f"Reference start: {item['reference_start']} s")
    print(f"Participant start: {item['participant_start']} s")
    print(f"Start-time difference: {item['start_difference']:+.2f} s")
    print(f"Reference duration: {item['reference_duration']} s")
    print(f"Participant duration: {item['participant_duration']} s")
    print(f"Duration difference: {item['duration_difference']:+.2f} s")

print("\nComparison completed.")
