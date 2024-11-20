import fnmatch
import os
import sys
from collections import defaultdict
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import webvtt


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
    dpi=100,
):
    fig_width = width / dpi
    fig_height = height / dpi

    plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
    podcasts = list(podcast_counts.keys())
    x = np.arange(len(podcasts))
    bar_width = 0.8 / len(keywords)

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

    for i, keyword in enumerate(keywords):
        counts = [normalized_counts[podcast][keyword] for podcast in podcasts]
        plt.bar(
            x + i * bar_width,
            counts,
            bar_width,
            label=f"'{keyword}'",
            alpha=0.75,
        )

    plt.title(title, fontsize=18, color="darkblue", fontweight="bold", loc="center")
    plt.xlabel("Podcasts")
    plt.ylabel("Keyword Frequency (per episode)")
    plt.xticks(x + bar_width * (len(keywords) / 2), podcasts, rotation=45, ha="right")
    plt.legend()

    # Add footer text.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_transcripts = sum(episode_counts.values())
    footer_text = (
        f"Generated on: {timestamp}\nTranscripts analyzed: {total_transcripts}"
    )
    plt.text(
        1.0,
        -0.2,
        footer_text,
        fontsize=10,
        color="gray",
        transform=plt.gca().transAxes,
        ha="right",
        va="top",
    )

    # Save to file.
    plt.tight_layout()
    plt.savefig(output_image)
    print(f"Plot saved as {output_image}")


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
