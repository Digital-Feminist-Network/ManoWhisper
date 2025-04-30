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


def classify_hate(sentences, model_pipeline):
    """Classifies hate and nothate scores for each sentence."""
    hate_scores = []
    not_hate_scores = []

    with alive_bar(len(sentences), title="Processing Sentences") as bar:
        for sentence in sentences:
            result = model_pipeline(sentence)

            # Default scores.
            hate_score = 0
            not_hate_score = 0

            # Extract scores based on label.
            for entry in result:
                if entry["label"] == "hate":
                    # Negative for hate.
                    hate_score = -entry["score"]
                elif entry["label"] == "nothate":
                    not_hate_score = entry["score"]

            hate_scores.append(hate_score)
            not_hate_scores.append(not_hate_score)
            bar()

    return hate_scores, not_hate_scores


def plot_dual_axis_chart(
    timestamps, hate_scores, not_hate_scores, output_filename, title
):
    """Generate a dual-axis area chart with Plotly."""

    # Convert timestamps to minutes.
    time_in_minutes = [
        sum(float(x) * 60**i for i, x in enumerate(reversed(ts.split(":")))) / 60
        for ts in timestamps
    ]

    # Create the chart.
    fig = go.Figure()

    # Add "nothate" area (positive y-axis).
    fig.add_trace(
        go.Scatter(
            x=time_in_minutes,
            y=not_hate_scores,
            fill="tozeroy",
            mode="lines",
            line=dict(width=2),
            name="Not Hate Score",
        )
    )

    # Add "hate" area (negative y-axis).
    fig.add_trace(
        go.Scatter(
            x=time_in_minutes,
            y=hate_scores,
            fill="tozeroy",
            mode="lines",
            line=dict(width=2),
            name="Hate Score",
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
            ticktext=["1 (Hate)", "0.5", "0", "0.5", "1 (Not Hate)"],
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
    "--title", "-t", default="Hate Speech Analysis Chart", help="Title of the chart"
)
def main(input_vtt_file, output_html_file, title):
    """
    Generate a dual-axis chart of hate scores for a given WebVTT transcript.
    """
    sentences, timestamps = parse_vtt_file(input_vtt_file)

    model_pipeline = pipeline(
        "text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target"
    )

    hate_scores, not_hate_scores = classify_hate(sentences, model_pipeline)

    plot_dual_axis_chart(
        timestamps, hate_scores, not_hate_scores, output_html_file, title
    )


if __name__ == "__main__":
    main()
