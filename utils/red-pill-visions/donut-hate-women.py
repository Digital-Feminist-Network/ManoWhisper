import os
from datetime import datetime

import click
import plotly.graph_objects as go
import webvtt
from alive_progress import alive_bar
from transformers import pipeline


def parse_vtt_files(input_path):
    """
    Parse WebVTT files to extract sentences and timestamps.

    Handles both a directory of VTT files and a single VTT file.
    """
    sentences = []
    filenames = []

    if os.path.isdir(input_path):
        vtt_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".vtt")
        ]
    elif os.path.isfile(input_path) and input_path.endswith(".vtt"):
        vtt_files = [input_path]
    else:
        raise ValueError("Input must be a directory or a .vtt file.")

    for filepath in vtt_files:
        for caption in webvtt.read(filepath):
            sentences.append(caption.text.strip().replace("\n", " "))
            filenames.append(os.path.basename(filepath))

    return sentences, filenames


def classify_misogyny(sentences, model_pipeline):
    """Classifies misogyny and non-misogyny scores for each sentence."""
    misogyny_scores = []
    labels = []

    with alive_bar(len(sentences), title="Processing Sentences") as bar:
        for sentence in sentences:
            result = model_pipeline(sentence)

            # Default scores.
            misogynist_score = 0
            label = "non-misogynist"

            # Extract scores based on label.
            for entry in result:
                if entry["label"] == "misogynist":
                    misogynist_score = -entry["score"]
                    label = "misogynist"
                elif entry["label"] == "non-misogynist":
                    misogynist_score = entry["score"]
                    label = "non-misogynist"

            misogyny_scores.append(misogynist_score)
            labels.append(label)
            bar()

    return misogyny_scores, labels


def plot_pie_chart(labels, sentences, output_filename, title):
    """Generate a pie chart with Plotly."""

    # Count misogynist and non-misogynist occurrences.
    misogyny_count = labels.count("misogynist")
    non_misogynist_count = labels.count("non-misogynist")

    # Data for pie chart.
    values = [misogyny_count, non_misogynist_count]
    labels = ["Misogyny", "Non Misogyny"]
    custom_colors = ["#ff1b6b", "#45caff"]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo="percent+label",
            marker=dict(colors=custom_colors),
            textfont=dict(size=20, family="Arial", weight="bold"),
        )
    )

    # Update layout for pie chart.
    total_sentences = len(sentences)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = (
        f"Generated: {timestamp}<br />Sentences classified: {total_sentences:,}"
    )

    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=28, family="Arial", weight="bold"),
        },
        annotations=[
            {
                "x": 1,
                "y": -0.05,
                "xref": "paper",
                "yref": "paper",
                "text": footer_text,
                "showarrow": False,
                "font": dict(size=12, color="gray"),
                "align": "right",
            }
        ],
        height=1300,
        width=1500,
        margin=dict(l=50, r=50, t=200, b=100),
        showlegend=False,
    )

    # Save as an HTML file
    fig.write_html(output_filename)
    print(f"Pie chart saved as {output_filename}")


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_html_file", type=click.Path())
@click.option(
    "--title", "-t", default="Misogyny Analysis Chart", help="Title of the chart"
)
def main(input_path, output_html_file, title):
    """
    Generate a pie chart of misogynist vs non misogynist classifications for WebVTT transcripts.

    Accepts either a directory of VTT files or a single VTT file.
    """
    sentences, filenames = parse_vtt_files(input_path)

    model_pipeline = pipeline(
        "text-classification", model="MilaNLProc/bert-base-uncased-ear-misogyny"
    )

    misogyny_scores, labels = classify_misogyny(sentences, model_pipeline)

    plot_pie_chart(labels, sentences, output_html_file, title)


if __name__ == "__main__":
    main()
