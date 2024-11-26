import fnmatch
import os
import sys
from collections import defaultdict
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import webvtt
from plotly.subplots import make_subplots


def count_keywords_across_podcasts(podcast_paths, keywords):
    podcast_counts = defaultdict(lambda: defaultdict(int))
    episode_counts = {}

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

    return podcast_counts, episode_counts


def plot_keyword_trends_across_podcasts(
    podcast_counts,
    episode_counts,
    keywords,
    output_image,
    width,
    height,
    title,
):
    """
    Creates an interactive bar chart of keyword trends across podcasts using Plotly.
    """
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
        barmode="group",  # Grouped bar chart
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

    # Show the interactive chart in the browser.
    fig.show()


def main():
    if len(sys.argv) < 6:
        print(
            "Usage: python red-pill-resonator.py <keywords> <width_px> <height_px> <title> <output_image>"
        )
        sys.exit(1)

    # Podcasts.
    podcast_paths = {
        "Candace Owens": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/Candace Owens/vtt",
        "Loomer Unleashed": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/Loomer Unleashed/vtt",
        "Tate Speech": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/Tate Speech/vtt",
        "The Culture War Podcast with Tim Pool": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/The Culture War - Tim Pool/vtt",
        "The Jordan B. Peterson Podcast": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/The Jordan B. Peterson Podcast/vtt",
        "The StoneZONE with Roger Stone": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/The StoneZONE with Roger Stone/vtt",
        "The Tucker Carlson Show": "/home/nruest/Projects/digfemcan/podcast-analysis/mano-whisper/data/The Tucker Carlson Show/vtt",
    }

    # Command-line arguments.
    keywords = sys.argv[1].split(",")
    width = int(sys.argv[2])
    height = int(sys.argv[3])
    title = sys.argv[4]
    output_image = sys.argv[5]

    # Count keywords across podcasts and get episode counts.
    podcast_counts, episode_counts = count_keywords_across_podcasts(
        podcast_paths, keywords
    )

    # Plot keyword trends across podcasts.
    plot_keyword_trends_across_podcasts(
        podcast_counts, episode_counts, keywords, output_image, width, height, title
    )


if __name__ == "__main__":
    main()
