import re
from collections.abc import Iterable
from functools import partial

import numpy as np
import pandas as pd
import streamlit as st
from hyperscore import SCALES
from hyperscore.theory import ordered_from_scale

CHROMATIC_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_REGEX = re.compile(r"([A-G]#?)(\d+) \((\d+)\)")
DEFAULT_SCALE = st.query_params.get("default_scale")

# --------------------------------
# Utility functions
# --------------------------------


def midi_to_note(midi: int) -> tuple[str, int]:
    note = CHROMATIC_NOTES[midi % 12]
    octave = midi // 12 - 2  # C3 Rule (C3=60)
    return note, octave


def make_data(tuning_rev: list[int], fret_range: tuple[int, int]) -> np.ndarray:
    fret_start, fret_end = fret_range

    data = np.ndarray((len(tuning_rev), fret_end - fret_start), dtype=object)

    for i in range(len(tuning_rev)):
        root_midi = tuning_rev[i]

        for j in range(fret_start, fret_end):
            note_midi = root_midi + j
            note_name, note_octave = midi_to_note(note_midi)
            data[i, j - fret_start] = f"{note_name}{note_octave} ({note_midi})"

    return data


def highlight_cells(val: str, root: str, scale: list[str]) -> str:
    match = NOTE_REGEX.match(val)
    if not match:
        return ""  # bug

    color, bg_color = "", ""
    note_name, _, _ = match.groups()

    if note_name == root:
        color, bg_color = "black", "cyan"
    elif any(note_name == s for s in scale):
        color, bg_color = "white", "blue"

    return f"color: {color}; background-color: {bg_color}"


def make_df(
    scale: Iterable[int],
    *,
    tuning: list[int],
    fret_range: tuple[int, int],
    highlight_range: tuple[int, int],
):
    scale_str = [CHROMATIC_NOTES[x] for x in scale]
    tuning_rev = list(reversed(tuning))
    data = make_data(tuning_rev, fret_range)

    df = pd.DataFrame(data=data)

    subset = df.columns[0:1].union(
        df.columns[highlight_range[0] : highlight_range[1]]
    )  # open string and highlighted frets

    df = df.style.map(
        partial(highlight_cells, root=scale_str[0], scale=scale_str),
        subset=subset,
    )

    return df


# --------------------------------
# Streamlit UI
# --------------------------------

st.set_page_config(layout="wide")
col1, col2 = st.columns([1, 4])

with col1:
    st.title("fingerboard")

    tuning = st.text_input("Enter tuning (midi number)", value="40, 45, 50, 55, 59, 64")
    tuning = [int(x) for x in tuning.split(",")]

    fret_range_raw = st.slider(
        "Fret range:", min_value=0, max_value=24, value=(0, 15), step=1
    )
    fret_range = fret_range_raw[0], fret_range_raw[1] + 1  # make it inclusive

    highlight_range_raw = st.slider(
        "Highlight range:", min_value=0, max_value=24, value=(0, 24), step=1
    )
    highlight_range = (
        highlight_range_raw[0],
        highlight_range_raw[1] + 1,
    )  # make it inclusive

    n_fingerboards = st.slider(
        "Number of fingerboards:", min_value=1, max_value=5, step=1
    )

    scales = []
    for i in range(n_fingerboards):
        with st.expander(f"Fingerboard {i + 1}"):
            options = sorted(name for name in SCALES)
            index = options.index(DEFAULT_SCALE) if DEFAULT_SCALE in options else 0
            scale_name = st.selectbox(
                "Scale name:", options=options, index=index, key=f"scale_name{i}"
            )

            transpose = st.slider(
                "Transpose:", min_value=0, max_value=11, step=1, key=f"transpose{i}"
            )

            ordered = ordered_from_scale(SCALES[scale_name]).transpose(transpose)
            st.write(ordered.name)
            scales.append(ordered.pcs)


with col2:
    for scale in scales:
        df = make_df(
            scale,
            tuning=tuning,
            fret_range=fret_range,
            highlight_range=highlight_range,
        )
        st.dataframe(df)
