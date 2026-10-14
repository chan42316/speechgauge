
from src.speech_alignment import align_speech_audio

reference_path = r"C:\Users\CHANDRU\Downloads\example_fsc.wav"
participant_path = r"data\example_fsc_slower.wav"

try:
    result = align_speech_audio(
        reference_path,
        participant_path
    )

    points = result["aligned_points"]

    print("\n===== SPEECHGAUGE ALIGNMENT CHECK =====")
    print("Reference duration:", result["reference_duration"], "seconds")
    print("Participant duration:", result["participant_duration"], "seconds")
    print("Alignment cost:", result["alignment_cost"])
    print("Total aligned points:", len(points))

    if points:
        print("\nAlignment at selected positions:")

        indices = sorted(set([
            0,
            len(points) // 4,
            len(points) // 2,
            (3 * len(points)) // 4,
            len(points) - 1
        ]))

        for index in indices:
            point = points[index]

            print(
                f"Reference: {point['reference_time']:.2f}s | "
                f"Participant: {point['participant_time']:.2f}s"
            )

    print("\nAlignment check completed.")

except Exception as error:
    print("Alignment failed:", error)
