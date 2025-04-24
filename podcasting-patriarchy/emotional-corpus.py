import os
import time
from collections import defaultdict

import click
import gspread
import webvtt
from alive_progress import alive_bar
from oauth2client.service_account import ServiceAccountCredentials
from transformers import pipeline


def setup_google_sheets(sheet_id, keyfile_path, sheet_name):
    """Connect to Google Sheets and open the specified worksheet."""
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    return sheet


def parse_vtt_file(vtt_file):
    """Extract sentences from transcripts."""
    sentences = [
        caption.text.strip().replace("\n", " ") for caption in webvtt.read(vtt_file)
    ]
    return sentences


def classify_emotions(sentences, model_pipeline):
    aggregated_scores = defaultdict(float)
    total_sentences = len(sentences) or 1

    for sentence in sentences:
        results = model_pipeline(sentence)
        if results and isinstance(results[0], list):
            results = results[0]
        for entry in results:
            aggregated_scores[entry["label"]] += entry["score"]

    for emotion in aggregated_scores:
        aggregated_scores[emotion] /= total_sentences

    return aggregated_scores


@click.command()
@click.argument("vtt_directory", type=click.Path(exists=True))
@click.argument("keyfile_path", type=click.Path(exists=True))
@click.argument("sheet_id")
@click.argument("sheet_name")
def main(vtt_directory, keyfile_path, sheet_id, sheet_name):
    """
    Analyze emotions in podcast transcripts and store results in Google Sheets.

    Example usage:
      python emotional-corpus.py /path/to/vtt/files keyfile.json google_sheet_id sheet_name
    """
    sheet = setup_google_sheets(sheet_id, keyfile_path, sheet_name)
    model_pipeline = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None,
    )

    emotion_labels = [
        "anger",
        "disgust",
        "fear",
        "joy",
        "neutral",
        "sadness",
        "surprise",
    ]

    sheet.update(values=[["filename"] + emotion_labels], range_name="A1:H1")

    vtt_files = [f for f in os.listdir(vtt_directory) if f.endswith(".vtt")]

    with alive_bar(len(vtt_files), title="Processing transcripts") as bar:
        for vtt_file in vtt_files:
            file_path = os.path.join(vtt_directory, vtt_file)
            sentences = parse_vtt_file(file_path)
            emotion_scores = classify_emotions(sentences, model_pipeline)

            row = [vtt_file] + [
                round(emotion_scores.get(label, 0), 4) for label in emotion_labels
            ]
            sheet.append_row(row)

            bar()
            time.sleep(1)


if __name__ == "__main__":
    main()
