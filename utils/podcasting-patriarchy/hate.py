import csv as csv_module
import os
from datetime import datetime
from pathlib import Path

import click
import pandas as pd
import plotly.graph_objects as go
import webvtt
from alive_progress import alive_bar
from plotly.subplots import make_subplots
from transformers import pipeline


def extract_show_name(vtt_path):
    return Path(vtt_path).parent.name


def parse_vtt_files(input_path):
    sentences = []
    filenames = []

    vtt_files = [
        os.path.join(input_path, f)
        for f in os.listdir(input_path)
        if f.endswith(".vtt")
    ]
    for filepath in vtt_files:
        for caption in webvtt.read(filepath):
            text = caption.text.strip().replace("\n", " ")
            if text:
                sentences.append(text)
                filenames.append(filepath)

    return sentences, filenames


def classify_hate(sentences, model_pipeline):
    """Classifies hate and nothate scores for each sentence."""
    hate_scores = []
    labels = []

    with alive_bar(len(sentences), title="Classifying Hate Speech") as bar:
        for sentence in sentences:
            result = model_pipeline(sentence)

            hate_score = 0
            label = "nothate"

            for entry in result:
                if entry["label"] == "hate":
                    hate_score = entry["score"]
                    label = "hate"
                elif entry["label"] == "nothate":
                    hate_score = entry["score"]
                    label = "nothate"

            hate_scores.append(hate_score)
            labels.append(label)
            bar()

    return hate_scores, labels


def write_classification_to_csv(shows, output_csv):
    model_pipeline = pipeline(
        "text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target"
    )

    all_data = []
    for show_path in shows:
        show_name = os.path.basename(os.path.dirname(show_path))
        sentences, filenames = parse_vtt_files(show_path)
        scores, labels = classify_hate(sentences, model_pipeline)
        for fn, lbl, sc in zip(filenames, labels, scores):
            all_data.append(
                {"filename": fn, "label": lbl, "score": sc, "show": show_name}
            )

    df = pd.DataFrame(all_data)
    df.to_csv(output_csv, index=False)
    print(f"Saved CSV to {output_csv}")


def generate_faceted_pie_chart(df, output_html, title):
    summary = (
        df.groupby("show")["label"].value_counts().unstack(fill_value=0).reset_index()
    )
    summary.columns.name = None
    summary = summary.rename(
        columns={
            "hate": "Hate Speech",
            "nothate": "Non Hate Speech",
            "show": "Show",
        }
    )

    rows = (len(summary) + 2) // 3
    cols = 3
    specs = [[{"type": "domain"} for _ in range(cols)] for _ in range(rows)]

    fig = make_subplots(
        rows=rows,
        cols=cols,
        specs=specs,
        subplot_titles=summary["Show"].tolist(),
    )

    for idx, row in summary.iterrows():
        r = (idx // cols) + 1
        c = (idx % cols) + 1
        fig.add_trace(
            go.Pie(
                rotation=90,
                labels=["Hate Speech", "Non Hate Speech"],
                values=[row["Hate Speech"], row["Non Hate Speech"]],
                marker=dict(colors=["#9e2a2b", "#e09f3e"]),
                name=row["Show"],
                textinfo="label+percent",
            ),
            row=r,
            col=c,
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=28)),
        height=600 * rows,
        showlegend=False,
        annotations=[
            *fig["layout"]["annotations"],
            dict(
                x=1,
                y=-0.1,
                xref="paper",
                yref="paper",
                text=f"Generated: {timestamp}",
                showarrow=False,
                font=dict(size=12, color="gray"),
            ),
        ],
    )

    fig.write_html(output_html)
    print(f"Pie chart saved to {output_html}")


@click.group()
def cli():
    pass


@cli.command(name="csv")
@click.option(
    "--shows",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help="Paths to VTT folders",
)
@click.argument("output_csv", type=click.Path())
def csv_command(shows, output_csv):
    """Process VTT directories and output classification to CSV"""
    write_classification_to_csv(shows, output_csv)


@cli.command(name="graph")
@click.option("--title", "-t", default="Hate Classification", help="Chart title")
@click.option(
    "--csv",
    "csv_file",
    required=True,
    type=click.Path(exists=True),
    help="CSV file with classification data",
)
@click.argument("output_html_file", type=click.Path())
def graph_command(title, csv_file, output_html_file):
    """Generate a faceted pie chart from CSV"""
    df = pd.read_csv(csv_file)
    generate_faceted_pie_chart(df, output_html_file, title)


if __name__ == "__main__":
    cli()
