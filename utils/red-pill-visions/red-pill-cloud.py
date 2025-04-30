import os
from datetime import datetime

import click
import matplotlib.pyplot as plt
import nltk
import webvtt
from alive_progress import alive_bar
from nltk.corpus import stopwords
from wordcloud import WordCloud

nltk.download("stopwords")


def generate_wordcloud(
    text,
    output_path,
    file_count,
    width=800,
    height=400,
    title="Word Cloud",
    stop_words=None,
):
    wordcloud = WordCloud(
        width=width, height=height, background_color="white", stopwords=stop_words
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

    # Add metadata and pin it to the bottom-right corner.
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


def process_vtt_files(directory, additional_stopwords=None):
    stop_words = set(stopwords.words("english"))

    # Merge additional stopwords if provided.
    if additional_stopwords:
        stop_words.update(word.lower() for word in additional_stopwords)

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


@click.command()
@click.argument("vtt_directory", type=click.Path(exists=True))
@click.argument("output_image", type=click.Path())
@click.option("--width", default=800, help="Width of the wordcloud (default: 800)")
@click.option("--height", default=400, help="Height of the wordcloud (default: 400)")
@click.option("--title", default="Word Cloud", help="Title of the wordcloud")
@click.option(
    "--additional-stopwords",
    default="",
    help="Comma-separated list of additional stopwords to exclude",
)
def main(vtt_directory, output_image, width, height, title, additional_stopwords):
    """Generate a wordcloud from WebVTT files."""

    # Parse additional stopwords.
    additional_stopwords = (
        additional_stopwords.split(",") if additional_stopwords else None
    )

    # Process WebVTT files.
    text_corpus, file_count = process_vtt_files(vtt_directory, additional_stopwords)

    # Generate wordcloud.
    stop_words = set(stopwords.words("english"))
    if additional_stopwords:
        stop_words.update(additional_stopwords)

    generate_wordcloud(
        text_corpus,
        output_image,
        file_count,
        width,
        height,
        title,
        stop_words=stop_words,
    )


if __name__ == "__main__":
    main()
