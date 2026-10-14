
def generate_temporal_findings(
    reference_intervals,
    participant_intervals,
    start_time_tolerance=0.20,
    duration_tolerance=0.20,
):
    """
    Compare quiet intervals using nearest-start matching.

    Findings indicate possible timing differences, not confirmed speech flaws.
    Intervals are matched one-to-one; unmatched intervals are reported separately.
    """

    findings = []

    reference_intervals = sorted(
        reference_intervals or [],
        key=lambda item: item["start_seconds"]
    )
    participant_intervals = sorted(
        participant_intervals or [],
        key=lambda item: item["start_seconds"]
    )

    # Match each reference interval to the nearest unused participant interval.
    unmatched_participant = set(range(len(participant_intervals)))
    unmatched_reference = set(range(len(reference_intervals)))
    matches = []

    candidates = []

    for ref_index, reference in enumerate(reference_intervals):
        for part_index, participant in enumerate(participant_intervals):
            start_difference = (
                float(participant["start_seconds"])
                - float(reference["start_seconds"])
            )
            candidates.append(
                (abs(start_difference), ref_index, part_index)
            )

    for _, ref_index, part_index in sorted(candidates):
        if (
            ref_index not in unmatched_reference
            or part_index not in unmatched_participant
        ):
            continue

        reference = reference_intervals[ref_index]
        participant = participant_intervals[part_index]

        start_difference = round(
            float(participant["start_seconds"])
            - float(reference["start_seconds"]),
            2
        )

        duration_difference = round(
            float(participant["duration_seconds"])
            - float(reference["duration_seconds"]),
            2
        )

        # Avoid pairing clearly unrelated intervals.
        # This threshold is a matching heuristic, not proof of equivalence.
        if abs(start_difference) > max(
            1.0,
            float(start_time_tolerance) * 4
        ):
            continue

        matches.append((ref_index, part_index))
        unmatched_reference.remove(ref_index)
        unmatched_participant.remove(part_index)

        interval_number = len(matches)
        ref_start = float(reference["start_seconds"])
        part_start = float(participant["start_seconds"])

        if abs(start_difference) > start_time_tolerance:
            findings.append({
                "type": "quiet_interval_start_shift",
                "interval_number": interval_number,
                "reference_timestamp": ref_start,
                "participant_timestamp": part_start,
                "difference_seconds": start_difference,
                "description": (
                    f"Matched quiet interval starts "
                    f"{abs(start_difference):.2f} seconds "
                    f"{'later' if start_difference > 0 else 'earlier'} "
                    "in the participant recording."
                ),
                "interpretation": (
                    "A low-energy interval start differs. Verify the "
                    "corresponding phrase before interpreting it as a flaw."
                )
            })

        if abs(duration_difference) > duration_tolerance:
            findings.append({
                "type": "quiet_interval_duration_difference",
                "interval_number": interval_number,
                "reference_timestamp": ref_start,
                "participant_timestamp": part_start,
                "difference_seconds": duration_difference,
                "description": (
                    f"Matched quiet interval is "
                    f"{abs(duration_difference):.2f} seconds "
                    f"{'longer' if duration_difference > 0 else 'shorter'} "
                    "in the participant recording."
                ),
                "interpretation": (
                    "Low-energy duration differs; the interval may represent "
                    "a pause, quiet speech, or recording conditions."
                )
            })

    # Report unmatched participant intervals.
    for part_index in sorted(unmatched_participant):
        interval = participant_intervals[part_index]
        findings.append({
            "type": "additional_participant_quiet_interval",
            "interval_number": part_index + 1,
            "reference_timestamp": None,
            "participant_timestamp": float(interval["start_seconds"]),
            "difference_seconds": None,
            "description": (
                f"Unmatched participant quiet interval at "
                f"{float(interval['start_seconds']):.2f} seconds."
            ),
            "interpretation": (
                "No reference interval was matched. This may be an added "
                "pause or a detection mismatch; it is not proof of hesitation."
            )
        })

    # Report unmatched reference intervals.
    for ref_index in sorted(unmatched_reference):
        interval = reference_intervals[ref_index]
        findings.append({
            "type": "missing_participant_quiet_interval",
            "interval_number": ref_index + 1,
            "reference_timestamp": float(interval["start_seconds"]),
            "participant_timestamp": None,
            "difference_seconds": None,
            "description": (
                f"Unmatched reference quiet interval at "
                f"{float(interval['start_seconds']):.2f} seconds."
            ),
            "interpretation": (
                "No participant interval was matched. The pause may differ, "
                "or the detector may have missed it."
            )
        })

    return sorted(
        findings,
        key=lambda item: (
            item["participant_timestamp"]
            if item["participant_timestamp"] is not None
            else item["reference_timestamp"]
            if item["reference_timestamp"] is not None
            else float("inf")
        )
    )
