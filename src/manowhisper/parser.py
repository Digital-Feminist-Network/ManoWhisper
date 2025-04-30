import os
from pathlib import Path

import webvtt
from alive_progress import alive_bar


def extract_show_name(input_path):
    show_name = Path(input_path).parent.name
    return show_name


def extract_sentences_timestamps(input_path):
    """
    Parse WebVTT files to extract sentences and timestamps.

    Handles both a directory of WebVTT files and a single WebVTT file.
    """
    sentences = []
    filenames = []
    timestamps = []

    if os.path.isdir(input_path):
        vtt_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".vtt")
        ]
    elif os.path.isfile(input_path) and input_path.endswith(".vtt"):
        vtt_files = [input_path]
    else:
        raise ValueError("Input must be a directory or a .vtt file.")

    with alive_bar(len(vtt_files), title="Parsing WebVTT files") as bar:
        for filepath in vtt_files:
            for caption in webvtt.read(filepath):
                sentences.append(caption.text.strip().replace("\n", " "))
                filenames.append(os.path.basename(filepath))
                timestamps.append(caption.start)
            bar()

    return sentences, filenames, timestamps


def extract_fulltext(input_path):
    """
    Parse WebVTT files to extract full text.

    Handles both a directory of WebVTT files and a single WebVTT file.
    """
    fulltext = []
    transcript = []

    if os.path.isdir(input_path):
        vtt_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".vtt")
        ]
    elif os.path.isfile(input_path) and input_path.endswith(".vtt"):
        vtt_files = [input_path]
    else:
        raise ValueError("Input must be a directory or a .vtt file.")

    for filepath in vtt_files:
        for caption in webvtt.read(filepath):
            transcript.append(caption.text)
            fulltext = " ".join(transcript)

    return fulltext
