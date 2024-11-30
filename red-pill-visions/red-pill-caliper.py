"""
Analyze podcast transcripts (WebVTT) and generate histograms.

Usage:
    red-pill-caliper.py --transcripts </path/to/vtt/files> --podcast-name <podcast-name>

Arguments:
    transcripts      Path to the directory of WebVTT files
    podcast-name     Name of the podcast
"""

import argparse
import os
from datetime import datetime

import plotly.express as px
import webvtt
from alive_progress import alive_bar


def extract_text_from_vtt(vtt_file_path):
    """Extract text from a VTT file."""
    transcript = []
    for caption in webvtt.read(vtt_file_path):
        transcript.append(caption.text)
    return " ".join(transcript)


# Calculate various metrics for an episode.
def calculate_metrics(text, episode_length_minutes):
    sentences = text.split(".")
    words = text.split()
    unique_words = set(words)
    characters_with_spaces = len(text)
    characters_without_spaces = sum(len(word) for word in words)
    word_count = len(words)
    speaking_rate = (
        word_count / episode_length_minutes if episode_length_minutes > 0 else 0
    )

    return {
        "num_sentences": len(sentences),
        "word_count": word_count,
        "unique_words": len(unique_words),
        "characters_with_spaces": characters_with_spaces,
        "characters_without_spaces": characters_without_spaces,
        "speaking_rate": speaking_rate,
    }

# Generate histograms.
def generate_histogram(data, metric_name, x_label, title, output_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    episode_count = len(data)
    footer_text = f"Generated: {timestamp}<br />Episode count: {episode_count}"
    fig = px.histogram(data, x=metric_name, labels={metric_name: x_label})
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 32, "family": "Arial", "color": "black"},
        },
        xaxis=dict(
            title=x_label,
            title_font=dict(size=20, family="Arial", weight="bold"),
            tickfont=dict(size=16, family="Arial"),
        ),
        yaxis=dict(
            title="Frequency (episodes)",
            title_font=dict(size=20, family="Arial", weight="bold"),
            tickfont=dict(size=16, family="Arial"),
        ),
        height=1237.5,
        width=2200,
        margin=dict(l=50, r=50, t=100, b=150),
        annotations=[
            {
                "x": 1,
                "y": -0.08,
                "xref": "paper",
                "yref": "paper",
                "text": footer_text,
                "showarrow": False,
                "font": dict(size=12, color="gray"),
                "align": "right",
            }
        ],
    )
    fig.write_html(output_file)
    print(f"Saved {output_file}")

# Process a directory of WebVTT files.
def process_vtt_directory(vtt_directory, podcast_name):
    files = [f for f in os.listdir(vtt_directory) if f.endswith(".vtt")]

    results = []

    with alive_bar(len(files), title="Processing episodes", unit="episode") as bar:
        for file in files:
            vtt_path = os.path.join(vtt_directory, file)
            base_name = os.path.splitext(file)[0]

            # Extract text and episode length.
            text = extract_text_from_vtt(vtt_path)
            captions = list(webvtt.read(vtt_path))
            episode_length_seconds = captions[-1].end_in_seconds if captions else 0
            episode_length_minutes = episode_length_seconds / 60

            # Calculate metrics.
            metrics = calculate_metrics(text, episode_length_minutes)
            metrics["episode_length_minutes"] = episode_length_minutes
            metrics["episode"] = base_name
            results.append(metrics)
            bar()

    # Generate histograms for each metric.
    histograms = [
        (
            "episode_length_minutes",
            "Episode Length (minutes)",
            "Episode Lengths",
            "episode-length",
        ),
        ("num_sentences", "Number of Sentences", "Sentences per Episode", "sentences"),
        ("word_count", "Word Count", "Words per Episode", "word-count"),
        ("unique_words", "Unique Word Count", "Vocabulary Size", "vocab-size"),
        (
            "characters_with_spaces",
            "Character Count (with spaces)",
            "Character Count per Episode",
            "character-count",
        ),
        ("speaking_rate", "Words per Minute", "Speaking Rate", "speaking-rate"),
    ]

    for metric, x_label, title_suffix, filename_suffix in histograms:
        title = f"{podcast_name}: {title_suffix}"
        output_file = f"{podcast_name.lower().replace(' ', '-')}-{filename_suffix}.html"
        generate_histogram(results, metric, x_label, title, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze podcast transcripts and generate histograms."
    )
    parser.add_argument(
        "--transcripts",
        type=str,
        required=True,
        help="Path to the directory of WebVTT files",
    )
    parser.add_argument(
        "--podcast-name", type=str, required=True, help="Podcast name for graph titles"
    )
    args = parser.parse_args()

    process_vtt_directory(args.transcripts, args.podcast_name)
