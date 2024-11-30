"""
Generate keyword frequency graphs across a corpus of WebVTT files.

Usage:
    red-pill-resonator.py <keywords> <width_px> <height_px> <title> <output_image>

Arguments:
    keywords      Comma delimited list of keywords
    width         Width (pixels) of graph
    height        Height (pixels) of graph
    title         Title of graph
    output_image  Filename of graph
"""

import fnmatch
import os
import sys
from collections import defaultdict
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import webvtt
from alive_progress import alive_bar
from plotly.subplots import make_subplots


def count_keywords_across_podcasts(podcast_paths, keywords):
    podcast_counts = defaultdict(lambda: defaultdict(int))
    episode_counts = {}

    # Calculate total tasks (podcasts and their WebVTT files).
    total_files = sum(
        [
            len([f for f in os.listdir(directory) if f.endswith(".vtt")])
            for directory in podcast_paths.values()
        ]
    )

    # Initialize the progress bar for all files.
    with alive_bar(total_files, title="Processing podcasts and episodes") as bar:
        for podcast, directory in podcast_paths.items():
            if not os.path.exists(directory):
                print(f"Warning: Directory {directory} does not exist. Skipping...")
                continue

            files = [f for f in os.listdir(directory) if f.endswith(".vtt")]
            # Count episodes.
            episode_counts[podcast] = len(files)

            for filename in files:
                vtt_path = os.path.join(directory, filename)

                # Process each caption in the transcript.
                for caption in webvtt.read(vtt_path):
                    text = caption.text.lower()
                    words = text.split()

                    for keyword in keywords:
                        # Match phrases or single words.
                        if " " in keyword:
                            # Phrase matching.
                            if fnmatch.fnmatch(text, f"*{keyword.lower()}*"):
                                podcast_counts[podcast][keyword] += 1
                        else:
                            # Single word matching.
                            podcast_counts[podcast][keyword] += sum(
                                fnmatch.fnmatch(word, keyword.lower()) for word in words
                            )
                bar()

    return podcast_counts, episode_counts


# Create  bar chart of keyword trends across podcasts using Plotly.
def plot_keyword_trends_across_podcasts(
    podcast_counts,
    episode_counts,
    keywords,
    output_image,
    width,
    height,
    title,
):
    podcasts = list(podcast_counts.keys())
    total_transcripts = sum(episode_counts.values())

    # Normalize keyword counts by episode counts to account for discrepancies in episode counts across podcasts.
    normalized_counts = {}
    for podcast, counts in podcast_counts.items():
        normalized_counts[podcast] = {
            keyword: (
                (counts[keyword] / episode_counts[podcast])
                if episode_counts[podcast] > 0
                else 0
            )
            for keyword in keywords
        }

    # Create traces for each keyword.
    traces = []
    for i, keyword in enumerate(keywords):
        counts = [normalized_counts[podcast][keyword] for podcast in podcasts]
        traces.append(
            go.Bar(
                x=podcasts,
                y=counts,
                name=f"'{keyword}'",
                text=[f"{count:.2f}" for count in counts],
                textposition="auto",
            )
        )

    # Create the figure.
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    for trace in traces:
        fig.add_trace(trace)

    # Add footer.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = (
        f"Generated on: {timestamp}<br />Transcripts analyzed: {total_transcripts}"
    )

    # Update layout.
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=24, family="Arial", color="darkblue"),
        ),
        xaxis=dict(
            title="Podcasts",
            tickangle=45,
            tickfont=dict(size=14, family="Arial"),
        ),
        yaxis=dict(
            title="Keyword Frequency (per episode)",
            tickfont=dict(size=14, family="Arial"),
        ),
        barmode="group",
        margin=dict(l=50, r=50, t=100, b=150),
        height=height,
        width=width,
        annotations=[
            dict(
                x=1,
                y=-0.2,
                xref="paper",
                yref="paper",
                text=footer_text,
                showarrow=False,
                font=dict(size=12, color="gray"),
                align="right",
            )
        ],
    )

    # Save as HTML and static image.
    base_name, _ = os.path.splitext(output_image)
    html_filename = base_name + ".html"
    fig.write_html(html_filename)
    fig.write_image(output_image)

    print(f"Plot saved as {output_image} and {html_filename}")


def main():
    if len(sys.argv) < 6:
        print(
            "Usage: python red-pill-resonator.py <keywords> <width_px> <height_px> <title> <output_image>"
        )
        sys.exit(1)

    # Base path for podcasts.
    base_path = "/mnt/vol1/data_sets/digfem/podcast-analysis/media"

    # Podcasts and their corresponding paths.
    podcast_paths = {
        "America First - Nicholas J. Fuentes": os.path.join(
            base_path, "America First - Nicholas J. Fuentes/vtt"
        ),
        "Candace Owens": os.path.join(base_path, "Candace Owens/vtt"),
        "Firebrand - Matt Gaetz": os.path.join(base_path, "Firebrand - Matt Gaetz/vtt"),
        "Fresh & Fit": os.path.join(base_path, "Fresh & Fit/vtt"),
        "Get Off My Lawn - Gavin McInnes": os.path.join(
            base_path, "Get Off My Lawn - Gavin McInnes/vtt"
        ),
        "Loomer Unleashed": os.path.join(base_path, "Loomer Unleashed/vtt"),
        "Making Sense - Sam Harris": os.path.join(
            base_path, "Making Sense - Sam Harris/vtt"
        ),
        "RFK Jr. The Defender": os.path.join(base_path, "RFK Jr. The Defender/vtt"),
        "Stay Free - Russel Brand": os.path.join(
            base_path, "Stay Free - Russel Brand/vtt"
        ),
        "Tate Speech": os.path.join(base_path, "Tate Speech/vtt"),
        "The Ben Shapiro Show": os.path.join(base_path, "The Ben Shapiro Show/vtt"),
        "The Charlie Kirk Show": os.path.join(base_path, "The Charlie Kirk Show/vtt"),
        "The Culture War - Tim Pool": os.path.join(
            base_path, "The Culture War - Tim Pool/vtt"
        ),
        "The Joe Rogan Experience": os.path.join(
            base_path, "The Joe Rogan Experience/vtt"
        ),
        "The Jordan B. Peterson Podcast": os.path.join(
            base_path, "The Jordan B. Peterson Podcast/vtt"
        ),
        "The Roseanne Barr Podcast": os.path.join(
            base_path, "The Roseanne Barr Podcast/vtt"
        ),
        "The StoneZONE with Roger Stone": os.path.join(
            base_path, "The StoneZONE with Roger Stone/vtt"
        ),
        "The Tucker Carlson Show": os.path.join(
            base_path, "The Tucker Carlson Show/vtt"
        ),
        "Triggered - Donald Trump Jr": os.path.join(
            base_path, "Triggered - Donald Trump Jr/vtt"
        ),
        "Truth Podcast - Vivek Ramaswamy": os.path.join(
            base_path, "Truth Podcast - Vivek Ramaswamy/vtt"
        ),
    }

    keywords = sys.argv[1].split(",")
    width = int(sys.argv[2])
    height = int(sys.argv[3])
    title = sys.argv[4]
    output_image = sys.argv[5]

    podcast_counts, episode_counts = count_keywords_across_podcasts(
        podcast_paths, keywords
    )

    plot_keyword_trends_across_podcasts(
        podcast_counts, episode_counts, keywords, output_image, width, height, title
    )


if __name__ == "__main__":
    main()
