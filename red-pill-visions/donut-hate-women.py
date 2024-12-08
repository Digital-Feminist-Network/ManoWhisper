import os
from datetime import datetime

import click
import plotly.graph_objects as go
import webvtt
from alive_progress import alive_bar
from transformers import pipeline


def parse_vtt_files(directory):
    """
    Parse all WebVTT files in a directory to extract sentences and timestamps.
    """
    sentences = []
    filenames = []

    for filename in os.listdir(directory):
        if filename.endswith(".vtt"):
            filepath = os.path.join(directory, filename)
            for caption in webvtt.read(filepath):
                sentences.append(caption.text.strip().replace("\n", " "))
                filenames.append(filename)

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
@click.argument("input_directory", type=click.Path(exists=True, file_okay=False))
@click.argument("output_html_file", type=click.Path())
@click.option(
    "--title", "-t", default="Misogyny Analysis Chart", help="Title of the chart"
)
def main(input_directory, output_html_file, title):
    """
    Generate a pie chart of misogynist vs non misogynist classifications for all WebVTT transcripts in a directory.
    """
    sentences, filenames = parse_vtt_files(input_directory)

    model_pipeline = pipeline(
        "text-classification", model="MilaNLProc/bert-base-uncased-ear-misogyny"
    )

    misogyny_scores, labels = classify_misogyny(sentences, model_pipeline)

    plot_pie_chart(labels, sentences, output_html_file, title)


if __name__ == "__main__":
    main()
