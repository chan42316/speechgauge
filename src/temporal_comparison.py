
def compare_quiet_intervals(reference_intervals, participant_intervals):
    """
    Compare quiet intervals by their order in each recording.
    This assumes corresponding intervals appear in the same order.
    """

    comparisons = []
    shared_count = min(
        len(reference_intervals),
        len(participant_intervals)
    )

    for index in range(shared_count):
        reference = reference_intervals[index]
        participant = participant_intervals[index]

        comparisons.append({
            "interval_number": index + 1,
            "reference_start": reference["start_seconds"],
            "participant_start": participant["start_seconds"],
            "start_difference": round(
                participant["start_seconds"]
                - reference["start_seconds"], 2
            ),
            "reference_duration": reference["duration_seconds"],
            "participant_duration": participant["duration_seconds"],
            "duration_difference": round(
                participant["duration_seconds"]
                - reference["duration_seconds"], 2
            )
        })

    return comparisons
