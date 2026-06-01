from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from hyperscore import SCALES
from hyperscore.theory import ordered_from_scale
from matplotlib.axes import Axes

CHROMATIC_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
DEFAULT_SCALE = st.query_params.get("default_scale")

# --------------------------------
# Utility functions
# --------------------------------


def convert_to_radian(pcs: Iterable[int]) -> list[float]:
    return [np.pi / 6.0 * pc for pc in pcs]


def convert_to_circle_of_fifth(pcs: Iterable[int]) -> list[int]:
    chromatic = list(range(12))
    circle_of_fifth = [chromatic[i * 7 % 12] for i in range(12)]
    return [circle_of_fifth[pc] for pc in pcs]


def tie(xs: list) -> list:
    xs = sorted(xs)
    return [*xs, xs[0]]


def plot_n_circles(
    ax: Axes, scales: Iterable[Iterable[int]], use_circle_of_fifth: bool
) -> None:
    # --------------------------------
    # Prepare to plot
    # --------------------------------

    chromatic_pcs = list(range(12))

    labels = CHROMATIC_NOTES
    if use_circle_of_fifth:
        labels = [CHROMATIC_NOTES[i * 7 % 12] for i in range(12)]
        scales = [convert_to_circle_of_fifth(scale) for scale in scales]

    # --------------------------------
    # Plot circles
    # --------------------------------

    # Set lables etc.
    ax.set_theta_zero_location("N")  # type: ignore
    ax.set_theta_direction(-1)  # type: ignore
    ax.set_xticks(convert_to_radian(chromatic_pcs))
    ax.set_xticklabels(labels=labels)
    ax.set_yticklabels([])
    ax.spines["polar"].set_visible(False)

    # Plot points
    points = tie(convert_to_radian(chromatic_pcs))
    ax.plot(points, np.ones(len(points)), "o", linestyle="")

    # Plot circles
    for scale in scales:
        if len(list(scale)) <= 2:
            continue

        circle = tie(convert_to_radian(scale))
        ax.fill_between(circle, np.ones(len(circle)), alpha=0.5)


# --------------------------------
# Streamlit UI
# --------------------------------

st.set_page_config()
col1, col2 = st.columns([1, 2])

with col1:
    st.title("n-circles")

    use_circle_of_fifth = st.toggle("Use circle of fifth?")

    n_circles = st.slider("Number of circles:", min_value=1, max_value=5, step=1)

    scales = []
    for i in range(n_circles):
        with st.expander(f"Circle {i + 1}"):
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
    fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "polar"})
    plot_n_circles(ax, scales, use_circle_of_fifth)
    st.pyplot(fig)
    plt.close(fig)
