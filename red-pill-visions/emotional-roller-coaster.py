import os
import re
from datetime import datetime

import click
import numpy as np
import plotly.graph_objects as go
import webvtt
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


def classify_emotions(sentences, model_pipeline):
    """Classifies emotions for each sentence."""
    emotion_scores = []
    for sentence in sentences:
        result = model_pipeline(sentence)
        if isinstance(result, list) and isinstance(result[0], dict):
            emotion_scores.append({entry["label"]: entry["score"] for entry in result})
        else:
            print(f"Unexpected output for sentence: {sentence}")
            emotion_scores.append({})

    return emotion_scores


def plot_emotions_over_time(timestamps, emotion_scores, output_filename, title):
    """Generate heatmap with plotly."""

    # Convert timestamps to minutes
    time_in_minutes = [
        sum(float(x) * 60**i for i, x in enumerate(reversed(ts.split(":")))) / 60
        for ts in timestamps
    ]

    # Extract emotion labels and organize data into a 2D array.
    emotion_labels = [
        "anger",
        "disgust",
        "fear",
        "joy",
        "neutral",
        "sadness",
        "surprise",
    ]
    heatmap_data = []
    for label in emotion_labels:
        heatmap_data.append([score_dict.get(label, 0) for score_dict in emotion_scores])

    custom_colorscale = [
        [0.0, "#FFFFFF"],
        [0.2, "#CCCCCC"],
        [0.4, "#999999"],
        [0.6, "#666666"],
        [0.8, "#333333"],
        [1.0, "#000000"],
    ]

    # Create the heatmap.
    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data,
            x=time_in_minutes,
            y=emotion_labels,
            colorscale=custom_colorscale,
            colorbar=dict(title="Emotion Score"),
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
            # Adjust the interval for x-axis ticks (every 5 minutes).
            dtick=5,
        ),
        yaxis=dict(
            title="Emotion",
            title_font=dict(size=18, family="Arial", weight="bold"),
            tickfont=dict(size=12, family="Arial"),
        ),
        height=1237.5,
        width=2200,
        margin=dict(l=50, r=50, t=100, b=150),
        annotations=[
            {
                "x": 1,
                "y": -0.15,
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
    print(f"Heatmap saved as {output_filename}")


@click.command()
@click.argument("input_vtt_file", type=click.Path(exists=True, readable=True))
@click.argument("output_html_file", type=click.Path())
@click.option("--title", "-t", default="Emotion Heatmap", help="Title of the heatmap")
def main(input_vtt_file, output_html_file, title):
    """
    Generate a heatmap of emotions for a given WebVTT transcript.
    """

    sentences, timestamps = parse_vtt_file(input_vtt_file)

    model_pipeline = pipeline(
        "text-classification", model="j-hartmann/emotion-english-distilroberta-base"
    )

    emotion_scores = classify_emotions(sentences, model_pipeline)

    plot_emotions_over_time(timestamps, emotion_scores, output_html_file, title)


if __name__ == "__main__":
    main()
