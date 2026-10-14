
import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
from difflib import SequenceMatcher

from src.coach_feedback import generate_coach_feedback
from src.audio_features import extract_audio_features
from src.temporal_analysis import detect_quiet_intervals
from src.temporal_comparison import compare_quiet_intervals
from src.temporal_findings import generate_temporal_findings
from src.speech_alignment import align_speech_audio
from src.transcription import transcribe_audio


# -------------------- WORD TIMING COMPARISON --------------------

def compare_word_timings(reference_words, participant_words):
    """
    Compare word timestamps for text-matched words.
    Different, missing, and added word sequences are reported separately.
    """

    reference_text = [
        word["text"].strip().lower()
        for word in reference_words
    ]

    participant_text = [
        word["text"].strip().lower()
        for word in participant_words
    ]

    matcher = SequenceMatcher(
        None,
        reference_text,
        participant_text,
        autojunk=False
    )

    rows = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        ref_group = reference_words[i1:i2]
        part_group = participant_words[j1:j2]

        if tag == "equal":
            for ref_word, part_word in zip(ref_group, part_group):
                ref_duration = ref_word["end"] - ref_word["start"]
                part_duration = part_word["end"] - part_word["start"]

                rows.append({
                    "Status": "Matched",
                    "Reference Word": ref_word["text"],
                    "Participant Word": part_word["text"],
                    "Reference Start (s)": ref_word["start"],
                    "Participant Start (s)": part_word["start"],
                    "Start Difference (s)": round(
                        part_word["start"] - ref_word["start"], 2
                    ),
                    "Reference Duration (s)": round(ref_duration, 2),
                    "Participant Duration (s)": round(part_duration, 2),
                    "Duration Difference (s)": round(
                        part_duration - ref_duration, 2
                    )
                })

        else:
            ref_start = (
                min(word["start"] for word in ref_group)
                if ref_group else None
            )

            ref_end = (
                max(word["end"] for word in ref_group)
                if ref_group else None
            )

            part_start = (
                min(word["start"] for word in part_group)
                if part_group else None
            )

            part_end = (
                max(word["end"] for word in part_group)
                if part_group else None
            )

            status_labels = {
                "replace": "Text differs",
                "delete": "Missing in participant",
                "insert": "Added by participant"
            }

            rows.append({
                "Status": status_labels[tag],
                "Reference Word": " ".join(
                    word["text"] for word in ref_group
                ) or "—",
                "Participant Word": " ".join(
                    word["text"] for word in part_group
                ) or "—",
                "Reference Start (s)": ref_start,
                "Participant Start (s)": part_start,
                "Start Difference (s)": None,
                "Reference Duration (s)": (
                    round(ref_end - ref_start, 2)
                    if ref_start is not None else None
                ),
                "Participant Duration (s)": (
                    round(part_end - part_start, 2)
                    if part_start is not None else None
                ),
                "Duration Difference (s)": None
            })

    return rows


# -------------------- PAGE CONFIGURATION --------------------

st.set_page_config(
    page_title="SpeechGauge",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ SpeechGauge")
st.subheader("Counterpointing Speech Analytics & Temporal Flaw Finding")

st.write(
    "Compare a reference speech recording with a participant recording. "
    "Identify measurable timing differences and receive evidence-based "
    "suggestions for reviewing speech delivery."
)

st.info(
    "SpeechGauge is a prototype. It identifies potential differences, "
    "not definitive speech flaws. Quiet intervals are estimated from audio "
    "energy and may include silence or quiet speech. Word timestamps are "
    "model estimates. For meaningful results, both recordings should contain "
    "the same or substantially similar speech."
)


# -------------------- AUDIO UPLOAD --------------------

st.header("1. Upload Recordings")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Reference recording**")

    reference_file = st.file_uploader(
        "Upload reference audio",
        type=["wav", "mp3", "ogg", "flac", "m4a"],
        key="reference"
    )

with col2:
    st.markdown("**Participant recording**")

    participant_file = st.file_uploader(
        "Upload participant audio",
        type=["wav", "mp3", "ogg", "flac", "m4a"],
        key="participant"
    )

if reference_file is not None:
    st.audio(reference_file)

if participant_file is not None:
    st.audio(participant_file)


# -------------------- ANALYSIS --------------------

if reference_file is not None and participant_file is not None:

    if st.button("Analyze Recordings", type="primary"):

        try:
            with st.spinner(
                "Transcribing speech, extracting features, comparing timing, "
                "and aligning audio. This may take a little while..."
            ):

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir = Path(temp_dir)

                    reference_path = (
                        temp_dir
                        / f"reference{Path(reference_file.name).suffix}"
                    )

                    participant_path = (
                        temp_dir
                        / f"participant{Path(participant_file.name).suffix}"
                    )

                    reference_path.write_bytes(
                        reference_file.getvalue()
                    )

                    participant_path.write_bytes(
                        participant_file.getvalue()
                    )

                    # 1. Transcribe both recordings with word timestamps.
                    reference_words = transcribe_audio(reference_path)
                    participant_words = transcribe_audio(participant_path)

                    # 2. Extract acoustic measurements.
                    reference_features = extract_audio_features(
                        reference_path
                    )

                    participant_features = extract_audio_features(
                        participant_path
                    )

                    # 3. Detect approximate quiet intervals.
                    reference_intervals = detect_quiet_intervals(
                        reference_path
                    )

                    participant_intervals = detect_quiet_intervals(
                        participant_path
                    )

                    # 4. Generate preliminary temporal findings.
                    findings = generate_temporal_findings(
                        reference_intervals,
                        participant_intervals
                    )

                    # 5. Compare detected quiet intervals.
                    interval_comparisons = compare_quiet_intervals(
                        reference_intervals,
                        participant_intervals
                    )

                    # 6. Align the recordings acoustically.
                    alignment = align_speech_audio(
                        reference_path,
                        participant_path
                    )

                    # 7. Generate coaching feedback.
                    coach_feedback = generate_coach_feedback(
                        reference_features,
                        participant_features,
                        findings
                    )

            st.success("Analysis completed successfully.")

            # -------------------- RECORDING COMPARISON --------------------

            st.header("2. Recording Comparison")

            ref_duration = float(
                reference_features["duration_seconds"]
            )

            part_duration = float(
                participant_features["duration_seconds"]
            )

            duration_difference = part_duration - ref_duration

            duration_col1, duration_col2, duration_col3 = st.columns(3)

            duration_col1.metric(
                "Reference Duration",
                f"{ref_duration:.2f} s"
            )

            duration_col2.metric(
                "Participant Duration",
                f"{part_duration:.2f} s"
            )

            duration_col3.metric(
                "Duration Difference",
                f"{duration_difference:+.2f} s"
            )

            # -------------------- WORD-LEVEL COMPARISON --------------------

            st.header("3. Word-Level Transcription & Timing")

            st.caption(
                "Word timestamps are estimates from the transcription model. "
                "Timing differences are not automatically speech flaws."
            )

            transcript_col1, transcript_col2 = st.columns(2)

            with transcript_col1:
                st.subheader("Reference Transcription")

                if reference_words:
                    st.dataframe(
                        pd.DataFrame(reference_words),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.warning(
                        "No words were detected in the reference recording."
                    )

            with transcript_col2:
                st.subheader("Participant Transcription")

                if participant_words:
                    st.dataframe(
                        pd.DataFrame(participant_words),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.warning(
                        "No words were detected in the participant recording."
                    )

            if reference_words and participant_words:
                word_comparison = compare_word_timings(
                    reference_words,
                    participant_words
                )

                st.subheader("Word Timing Comparison")

                st.dataframe(
                    pd.DataFrame(word_comparison),
                    use_container_width=True,
                    hide_index=True
                )

                matched_count = sum(
                    1 for row in word_comparison
                    if row["Status"] == "Matched"
                )

                changed_count = sum(
                    1 for row in word_comparison
                    if row["Status"] != "Matched"
                )

                summary_col1, summary_col2 = st.columns(2)

                summary_col1.metric(
                    "Matched Word Entries",
                    matched_count
                )

                summary_col2.metric(
                    "Changed / Missing / Added Entries",
                    changed_count
                )

                st.caption(
                    "Start Difference = participant word start minus reference "
                    "word start. A positive value means the word starts later "
                    "in the participant recording's timeline; a negative value "
                    "means it starts earlier. This comparison does not yet "
                    "correct for leading silence or align each word using the "
                    "acoustic alignment path. Transcription mistakes and "
                    "repeated words can also affect matching."
                )

            else:
                st.warning(
                    "Word comparison requires detected words in both recordings."
                )

            # -------------------- SPEECH COACH FEEDBACK --------------------

            st.header("4. Speech Coach Feedback")

            st.write(
                "Each recommendation is based on the measurements available "
                "to the current prototype. A measured difference is not "
                "automatically a delivery problem."
            )

            if coach_feedback:
                for index, item in enumerate(coach_feedback, start=1):

                    with st.expander(
                        f"{index}. {item['category']} — {item['priority']}",
                        expanded=True
                    ):
                        st.write(
                            f"**Timestamp:** {item['timestamp']}"
                        )

                        st.write(
                            f"**Measured evidence:** {item['evidence']}"
                        )

                        st.write(
                            f"**Finding:** {item['observation']}"
                        )

                        st.write(
                            f"**Possible impact:** "
                            f"{item.get('possible_impact', 'Not assessed')}"
                        )

                        st.write(
                            f"**Recommended action:** "
                            f"{item.get('action', item.get('suggestion', 'Review the audio around this timestamp.'))}"
                        )

                        if item.get("technical_interpretation"):
                            st.caption(
                                "Technical interpretation: "
                                f"{item['technical_interpretation']}"
                            )

            else:
                st.info(
                    "The current rules did not produce coaching feedback."
                )

            # -------------------- ACOUSTIC FEATURE COMPARISON --------------------

            st.header("5. Acoustic Feature Comparison")

            feature_labels = [
                (
                    "estimated_active_audio_seconds",
                    "Estimated Active Audio (s)"
                ),
                (
                    "pause_count",
                    "Estimated Quiet Interval Count"
                ),
                (
                    "mean_pitch_hz",
                    "Mean Estimated Pitch (Hz)"
                ),
                (
                    "pitch_variation_hz",
                    "Pitch Variation (Hz)"
                )
            ]

            feature_rows = []

            for key, label in feature_labels:
                ref_value = reference_features.get(key)
                part_value = participant_features.get(key)

                if ref_value is not None and part_value is not None:
                    try:
                        difference = round(
                            float(part_value) - float(ref_value), 2
                        )
                    except (TypeError, ValueError):
                        difference = None
                else:
                    difference = None

                feature_rows.append({
                    "Feature": label,
                    "Reference": ref_value,
                    "Participant": part_value,
                    "Difference": difference
                })

            st.dataframe(
                pd.DataFrame(feature_rows),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Pitch and active-audio measurements are estimates. "
                "Differences alone do not establish speaking quality, "
                "confidence, or emotion."
            )

            # -------------------- QUIET INTERVAL COMPARISON --------------------

            st.header("6. Quiet Interval Comparison")

            if interval_comparisons:
                st.dataframe(
                    pd.DataFrame(interval_comparisons),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(
                    "No corresponding quiet intervals were detected "
                    "for comparison."
                )

            # -------------------- TIMESTAMPED FINDINGS --------------------

            st.header("7. Timestamped Findings")

            if findings:
                st.write(
                    f"**{len(findings)} preliminary finding(s)** were "
                    "generated by the current temporal analysis."
                )

                for index, finding in enumerate(findings, start=1):

                    with st.expander(
                        f"Finding {index}: "
                        f"{finding.get('type', 'Timing Difference')}",
                        expanded=False
                    ):
                        st.write(
                            finding.get(
                                "description",
                                "A possible timing difference was detected."
                            )
                        )

                        st.write(
                            "**Reference timestamp:** "
                            f"{finding.get('reference_timestamp', 'Unavailable')}"
                        )

                        st.write(
                            "**Participant timestamp:** "
                            f"{finding.get('participant_timestamp', 'Unavailable')}"
                        )

                        st.write(
                            "**Difference (seconds):** "
                            f"{finding.get('difference_seconds', 'Unavailable')}"
                        )

                        st.caption(
                            finding.get(
                                "interpretation",
                                "Review the corresponding audio sections "
                                "before drawing conclusions."
                            )
                        )

            else:
                st.info(
                    "No timing differences crossed the current thresholds. "
                    "This does not guarantee equivalent delivery."
                )

            # -------------------- ACOUSTIC ALIGNMENT --------------------

            st.header("8. Acoustic Alignment")

            alignment_cost = alignment.get("alignment_cost")
            aligned_points = alignment.get("aligned_points", [])

            align_col1, align_col2 = st.columns(2)

            if alignment_cost is not None:
                align_col1.metric(
                    "Normalized Alignment Cost",
                    f"{float(alignment_cost):.4f}"
                )
            else:
                align_col1.metric(
                    "Normalized Alignment Cost",
                    "Unavailable"
                )

            align_col2.metric(
                "Aligned Frame Points",
                len(aligned_points)
            )

            st.caption(
                "Alignment uses MFCC features and Dynamic Time Warping. "
                "Alignment cost is not an accuracy score or a delivery-quality "
                "score. The current temporal finding generator does not yet "
                "use the alignment path to match quiet intervals or word times."
            )

            if aligned_points:
                st.write("Selected Alignment Timestamps")

                indices = sorted(set([
                    0,
                    len(aligned_points) // 4,
                    len(aligned_points) // 2,
                    (3 * len(aligned_points)) // 4,
                    len(aligned_points) - 1
                ]))

                selected_points = [
                    aligned_points[index] for index in indices
                ]

                st.dataframe(
                    pd.DataFrame(selected_points),
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as error:
            st.error(
                "Analysis failed. Check the traceback below to identify "
                "the cause."
            )
            st.exception(error)

else:
    st.info(
        "Upload both recordings to enable the analysis."
    )


# -------------------- FOOTER --------------------

st.divider()

st.caption(
    "SpeechGauge | Prototype | Acoustic differences are evidence for review, "
    "not definitive judgments of speaking quality."
)
