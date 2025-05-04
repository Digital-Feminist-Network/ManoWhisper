import os

import webvtt
from alive_progress import alive_bar

from manowhisper import parser


def calculate_metrics(text, episode_length_minutes):
    """Calculate various metrics for an episode."""
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
        "episodes": "",
        "num_sentences": len(sentences),
        "word_count": word_count,
        "unique_words": len(unique_words),
        "characters_with_spaces": characters_with_spaces,
        "characters_without_spaces": characters_without_spaces,
        "speaking_rate": speaking_rate,
    }


def process_podcast(input_path, show_name):
    """Process a directory of WebVTT files."""
    results = []
    files = [f for f in os.listdir(input_path) if f.endswith(".vtt")]


    with alive_bar(len(files), title="Processing episodes", unit="episode") as bar:
        for file in files:
            transcript_path = os.path.join(input_path, file)
            base_name = os.path.splitext(file)[0]

            # Extract text and episode length.
            text = parser.extract_fulltext(transcript_path)
            captions = list(webvtt.read(transcript_path))
            episode_length_seconds = captions[-1].end_in_seconds if captions else 0
            episode_length_minutes = episode_length_seconds / 60

            # Calculate metrics.
            metrics = calculate_metrics(text, episode_length_minutes)
            metrics["episodes"] = len(files)
            metrics["episode_length_minutes"] = episode_length_minutes
            metrics["episode"] = base_name
            results.append(metrics)
            bar()

    return results
