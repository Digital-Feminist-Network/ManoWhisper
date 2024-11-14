import os
import sys

import matplotlib.pyplot as plt
import nltk
import webvtt
from nltk.corpus import stopwords
from wordcloud import WordCloud

nltk.download("stopwords")


def generate_wordcloud(text, output_path, width=800, height=400, title="Word Cloud"):
    wordcloud = WordCloud(
        width=width, height=height, background_color="white"
    ).generate(text)

    # Plot the word cloud with title.
    plt.figure(figsize=(width / 100, height / 100), dpi=100)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(title, fontsize=20)

    # Save to file.
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Wordcloud saved to {output_path}")


def process_vtt_files(directory):
    stop_words = set(stopwords.words("english"))

    # Collect text from all VTT files in directory.
    full_text = []
    for filename in os.listdir(directory):
        if filename.endswith(".vtt"):
            vtt_path = os.path.join(directory, filename)
            print(f"Processing {vtt_path}")
            for caption in webvtt.read(vtt_path):
                # Split caption text into words and remove stopwords.
                words = [
                    word
                    for word in caption.text.split()
                    if word.lower() not in stop_words
                ]
                # Join filtered words back to text and add to corpus.
                full_text.append(" ".join(words))

    # Return the full corpus as a single string.
    return " ".join(full_text)


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python red-pill-cloud.py <vtt_directory> <output_image> [width] [height] [title]"
        )
        sys.exit(1)

    # Command-line arguments.
    vtt_directory = sys.argv[1]
    output_image = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    title = sys.argv[5] if len(sys.argv) > 5 else "Word Cloud"

    # Process VTT files to get text corpus.
    text_corpus = process_vtt_files(vtt_directory)

    # Generate and save word cloud.
    generate_wordcloud(text_corpus, output_image, width, height, title)


if __name__ == "__main__":
    main()
