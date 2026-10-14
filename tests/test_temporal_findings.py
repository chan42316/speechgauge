
from src.temporal_analysis import detect_quiet_intervals
from src.temporal_findings import generate_temporal_findings

reference_path = r"C:\Users\CHANDRU\Downloads\example_fsc.wav"
participant_path = r"data\example_fsc_slower.wav"

try:
    reference_intervals = detect_quiet_intervals(reference_path)
    participant_intervals = detect_quiet_intervals(participant_path)

    findings = generate_temporal_findings(
        reference_intervals,
        participant_intervals
    )

    print("\n===== SPEECHGAUGE TEMPORAL FINDINGS =====")

    if not findings:
        print("No differences exceeded the configured tolerances.")

    for index, finding in enumerate(findings, start=1):
        print(f"\nFinding {index}: {finding['type']}")
        print(f"Description: {finding['description']}")
        print(f"Reference timestamp: {finding['reference_timestamp']}")
        print(f"Participant timestamp: {finding['participant_timestamp']}")
        print(f"Difference: {finding['difference_seconds']}")
        print(f"Interpretation: {finding['interpretation']}")

    print(f"\nTotal findings: {len(findings)}")

except Exception as error:
    print("Analysis failed:", error)
