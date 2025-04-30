import os
from datetime import datetime

import click
import plotly.graph_objects as go
import webvtt
from alive_progress import alive_bar
from transformers import pipeline


def parse_vtt_file(vtt_file):
    """
    Parse a WebVTT file to extract sentences and their start times.
    """
    sentences = []
    timestamps = []

    for caption in webvtt.read(vtt_file):
        sentences.append(caption.text.strip().replace("\n", " "))
        timestamps.append(caption.start)

    return sentences, timestamps


def classify_misogyny(sentences, model_pipeline):
    """Classifies misogyny and non-misogyny scores for each sentence."""
    misogyny_scores = []
    non_misogyny_scores = []

    with alive_bar(len(sentences), title="Processing Sentences") as bar:
        for sentence in sentences:
            result = model_pipeline(sentence)

            # Default scores.
            misogynist_score = 0
            non_misogynist_score = 0

            # Extract scores based on label.
            for entry in result:
                if entry["label"] == "misogynist":
                    # Negative for misogynistic.
                    misogynist_score = -entry["score"]
                elif entry["label"] == "non-misogynist":
                    non_misogynist_score = entry["score"]

            misogyny_scores.append(misogynist_score)
            non_misogyny_scores.append(non_misogynist_score)
            bar()

    return misogyny_scores, non_misogyny_scores


def plot_dual_axis_chart(
    timestamps, misogyny_scores, non_misogyny_scores, output_filename, title
):
    """Generate a dual-axis area chart with Plotly."""

    # Convert timestamps to minutes.
    time_in_minutes = [
        sum(float(x) * 60**i for i, x in enumerate(reversed(ts.split(":")))) / 60
        for ts in timestamps
    ]

    # Create the chart.
    fig = go.Figure()

    # Add "non-misogynistic" area (positive y-axis).
    fig.add_trace(
        go.Scatter(
            x=time_in_minutes,
            y=non_misogyny_scores,
            fill="tozeroy",
            mode="lines",
            line=dict(width=2),
            name="Non-Misogynistic Score",
        )
    )

    # Add "misogynistic" area (negative y-axis).
    fig.add_trace(
        go.Scatter(
            x=time_in_minutes,
            y=misogyny_scores,
            fill="tozeroy",
            mode="lines",
            line=dict(width=2),
            name="Misogynistic Score",
        )
    )

    # Timestamp and footer.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = f"Generated: {timestamp}"

    # Layout and labels.
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=28, family="Arial", weight="bold"),
        },
        xaxis=dict(
            title="Time (minutes)",
            title_font=dict(size=18, family="Arial", weight="bold"),
            tickangle=45,
            tickfont=dict(size=12, family="Arial"),
            dtick=5,
        ),
        yaxis=dict(
            title="Score",
            title_font=dict(size=18, family="Arial", weight="bold"),
            tickfont=dict(size=12, family="Arial"),
            range=[-1, 1],
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["1 (Misogynistic)", "0.5", "0", "0.5", "1 (Non-Misogynistic)"],
        ),
        height=1357.5,
        width=2200,
        margin=dict(l=50, r=50, t=100, b=175),
        annotations=[
            {
                "x": 1,
                "y": -0.1,
                "xref": "paper",
                "yref": "paper",
                "text": footer_text,
                "showarrow": False,
                "font": dict(size=12, color="gray"),
                "align": "right",
            }
        ],
    )

    # Save as an HTML file.
    fig.write_html(output_filename)
    print(f"Dual-axis area chart saved as {output_filename}")


@click.command()
@click.argument("input_vtt_file", type=click.Path(exists=True, readable=True))
@click.argument("output_html_file", type=click.Path())
@click.option(
    "--title", "-t", default="Misogyny Analysis Chart", help="Title of the chart"
)
def main(input_vtt_file, output_html_file, title):
    """
    Generate a dual-axis chart of misogyny scores for a given WebVTT transcript.
    """
    sentences, timestamps = parse_vtt_file(input_vtt_file)

    model_pipeline = pipeline(
        "text-classification", model="MilaNLProc/bert-base-uncased-ear-misogyny"
    )

    misogyny_scores, non_misogyny_scores = classify_misogyny(sentences, model_pipeline)

    plot_dual_axis_chart(
        timestamps, misogyny_scores, non_misogyny_scores, output_html_file, title
    )


if __name__ == "__main__":
    main()
