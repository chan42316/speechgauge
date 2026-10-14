
def _format_timestamp(value):
    """Format seconds as MM:SS.ss."""
    if value is None:
        return "Unavailable"

    try:
        seconds = max(0.0, float(value))
        minutes = int(seconds // 60)
        remaining = seconds % 60
        return f"{minutes:02d}:{remaining:05.2f}"
    except (TypeError, ValueError):
        return str(value)


def generate_coach_feedback(
    reference_features,
    participant_features,
    temporal_findings
):
    """Generate transparent, evidence-based timing feedback."""

    feedback = []

    ref_duration = float(
        reference_features.get("duration_seconds", 0) or 0
    )
    part_duration = float(
        participant_features.get("duration_seconds", 0) or 0
    )

    # 1. Overall duration comparison.
    if ref_duration > 0 and part_duration > 0:
        difference = part_duration - ref_duration
        percentage = difference / ref_duration * 100

        # Flag meaningful duration differences without treating them
        # as proof of poor speaking.
        if abs(percentage) >= 10:
            if difference > 0:
                observation = (
                    "The participant recording is longer than the reference."
                )
                action = (
                    "Compare corresponding phrases in both recordings. "
                    "Check whether the extra time comes from longer pauses "
                    "or slower phrase delivery. Practise only sections that "
                    "sound unnecessarily prolonged, while retaining natural pauses."
                )
            else:
                observation = (
                    "The participant recording is shorter than the reference."
                )
                action = (
                    "Compare corresponding phrases in both recordings. "
                    "Check whether words are rushed or meaningful pauses "
                    "have been shortened. Practise those sections while "
                    "maintaining clarity and natural phrasing."
                )

            feedback.append({
                "category": "Overall timing",
                "priority": (
                    "Review" if abs(percentage) < 20 else "High difference"
                ),
                "timestamp": "Whole recording",
                "evidence": (
                    f"Reference: {ref_duration:.2f}s; "
                    f"participant: {part_duration:.2f}s; "
                    f"difference: {difference:+.2f}s "
                    f"({percentage:+.1f}%)."
                ),
                "observation": observation,
                "possible_impact": (
                    "The overall recording duration differs. This can reflect "
                    "pacing, pause placement, speech content, or recording "
                    "conditions; duration alone cannot identify the cause."
                ),
                "action": action,
                "technical_interpretation": (
                    "Measured duration difference; not a confirmed speaking flaw."
                ),
            })

    # 2. Phrase and quiet-interval findings.
    for finding in temporal_findings or []:
        finding_type = str(
            finding.get("type", "timing_difference")
        ).lower()

        description = finding.get(
            "description",
            "A possible timing difference was detected."
        )

        ref_time = finding.get("reference_timestamp")
        part_time = finding.get("participant_timestamp")
        difference_seconds = finding.get("difference_seconds")

        timestamp = (
            _format_timestamp(part_time)
            if part_time is not None
            else "Timestamp unavailable"
        )

        evidence_parts = [str(description)]

        if ref_time is not None:
            evidence_parts.append(
                f"Reference position: {_format_timestamp(ref_time)}."
            )

        if part_time is not None:
            evidence_parts.append(
                f"Participant position: {_format_timestamp(part_time)}."
            )

        if difference_seconds is not None:
            try:
                evidence_parts.append(
                    f"Measured difference: "
                    f"{float(difference_seconds):+.2f}s."
                )
            except (TypeError, ValueError):
                pass

        if "start_shift" in finding_type:
            observation = (
                "A detected low-energy interval begins at a different "
                "time in the two recordings."
            )
            possible_impact = (
                "This may reflect a different pause or phrase transition. "
                "The measurement alone cannot establish whether delivery "
                "is worse."
            )

            try:
                shift = float(difference_seconds)
            except (TypeError, ValueError):
                shift = 0.0

            direction = "later" if shift > 0 else "earlier"

            action = (
                f"Replay both recordings around {timestamp}. Check whether "
                f"the transition occurs {direction} in the participant audio. "
                "Practise that transition only if listening confirms that "
                "the timing is unsuitable."
            )

        elif "duration" in finding_type:
            observation = (
                "A detected low-energy interval has a different duration."
            )
            possible_impact = (
                "The difference may represent a pause, quiet speech, "
                "or a recording-related effect."
            )
            action = (
                f"Replay both recordings around {timestamp}. If the pause "
                "interrupts the phrase unnecessarily, practise adjusting "
                "it slightly. Retain pauses that support breathing or meaning."
            )

        elif "additional_participant" in finding_type:
            observation = (
                "An extra low-energy interval was detected in the participant audio."
            )
            possible_impact = (
                "It may be an added pause, but the detector cannot confirm "
                "that the speaker hesitated."
            )
            action = (
                f"Replay the participant audio around {timestamp}. Check "
                "whether the interval falls between spoken phrases and "
                "whether it disrupts the intended delivery."
            )

        elif "missing_participant" in finding_type:
            observation = (
                "A reference low-energy interval has no matched participant interval."
            )
            possible_impact = (
                "The participant may have used a shorter pause, or the "
                "interval detector may not have found the corresponding interval."
            )
            action = (
                "Compare both recordings around the reference timestamp. "
                "Check whether the participant's phrase transition remains clear."
            )

        else:
            observation = (
                "The timing analysis detected a possible interval mismatch."
            )
            possible_impact = (
                "The difference may reflect delivery timing, speech content, "
                "recording conditions, or imperfect interval matching."
            )
            action = (
                f"Replay both recordings around {timestamp} and verify "
                "the corresponding words and phrase boundaries before "
                "changing the delivery."
            )

        feedback.append({
            "category": "Pause and timing",
            "priority": "Review",
            "timestamp": timestamp,
            "evidence": " ".join(evidence_parts),
            "observation": observation,
            "possible_impact": possible_impact,
            "action": action,
            "technical_interpretation": finding.get(
                "interpretation",
                "Preliminary audio-based finding; verify by listening."
            ),
        })

    # 3. Avoid claiming that undetected differences mean perfect speech.
    if not feedback:
        feedback.append({
            "category": "Initial assessment",
            "priority": "Review",
            "timestamp": "Whole recording",
            "evidence": (
                "The current rules did not flag a major duration or "
                "quiet-interval difference."
            ),
            "observation": (
                "No major timing difference was identified by the current rules."
            ),
            "possible_impact": (
                "This does not establish that pronunciation, clarity, "
                "or phrase delivery matches the reference."
            ),
            "action": (
                "Listen to both recordings and compare corresponding phrases, "
                "word clarity, transitions, and natural pacing. These qualities "
                "are not fully evaluated by the current timing rules."
            ),
        })

    # Sort major measured differences first.
    feedback.sort(
        key=lambda item: (
            item["priority"] != "High difference",
            item["category"] == "Overall timing",
        )
    )

    return feedback
