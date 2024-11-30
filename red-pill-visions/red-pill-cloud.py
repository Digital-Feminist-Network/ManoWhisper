"""
Generate a wordcloud from a directory of WebVTT files.

Usage:
    python red-pill-cloud.py <vtt_directory> <output_image> [width] [height] [title]

Arguments:
    vtt_directory     Path to the directory of WebVTT files
    output_image      Filename of wordcloud
    width             Width (pixels) of wordcloud - defaults to 800
    height            Height (pixels of wordcloud - defaults to 400
    title             Title of wordcloud - defaults to "Word Cloud"
"""

import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import nltk
import webvtt
from alive_progress import alive_bar
from nltk.corpus import stopwords
from wordcloud import WordCloud

nltk.download("stopwords")


def generate_wordcloud(
    text, output_path, file_count, width=800, height=400, title="Word Cloud"
):
    wordcloud = WordCloud(
        width=width, height=height, background_color="white"
    ).generate(text)

    # Generate metadata.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata_text = f"Generated: {timestamp}\nTranscripts: {file_count}"

    # Plot the word cloud.
    plt.figure(figsize=(width / 100, height / 100 + 1), dpi=100)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    # Add title above the word cloud.
    plt.title(
        "\n" + title + "\n",
        fontsize=36,
        color="darkblue",
        fontweight="bold",
    )

    # Add metadata pinned to the bottom-right corner.
    plt.figtext(
        0.90,  # X-coordinate (right-aligned)
        0.10,  # Y-coordinate (bottom of the figure)
        metadata_text,
        horizontalalignment="right",
        fontsize=10,
        color="gray",
        wrap=True,
    )

    # Save to file.
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Wordcloud saved to {output_path}")


def process_vtt_files(directory):
    stop_words = set(stopwords.words("english"))

    # Collect text from all VTT files in directory.
    full_text = []
    vtt_files = [f for f in os.listdir(directory) if f.endswith(".vtt")]
    file_count = len(vtt_files)

    # Use alive-progress to show progress.
    with alive_bar(file_count, title="Processing VTT Files") as bar:
        for filename in vtt_files:
            vtt_path = os.path.join(directory, filename)
            for caption in webvtt.read(vtt_path):
                # Split caption text into words and remove stopwords.
                words = [
                    word
                    for word in caption.text.split()
                    if word.lower() not in stop_words
                ]
                # Join filtered words back to text and add to corpus.
                full_text.append(" ".join(words))
            bar()  # Increment progress bar

    # Return the full corpus as a single string and file count.
    return " ".join(full_text), file_count


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python red-pill-cloud.py <vtt_directory> <output_image> [width] [height] [title]"
        )
        sys.exit(1)

    vtt_directory = sys.argv[1]
    output_image = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    title = sys.argv[5] if len(sys.argv) > 5 else "Word Cloud"

    text_corpus, file_count = process_vtt_files(vtt_directory)

    generate_wordcloud(text_corpus, output_image, file_count, width, height, title)


if __name__ == "__main__":
    main()
