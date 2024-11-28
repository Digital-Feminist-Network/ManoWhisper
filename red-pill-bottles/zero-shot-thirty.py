"""
Process a directory of WebVTT files and do zero shot classification content with facebook/bart-large-mnli.

Usage:
    zero-shot-thirty.py --candidate-labels "label 1,label 2,label 3" /path/to/vtt/files output.csv

Arguments:
    candidate-labels   Comma-separated list of candidate labels for classification, e.g., "label 1,label 2,label 3".
    vtt_directory      Path to the directory containing WebVTT files.
    output_file        Path to the output CSV file where results will be saved.
"""

import argparse
import os

import pandas as pd
import webvtt
from alive_progress import alive_bar
from transformers import pipeline

zero_shot_classifier = pipeline(
    "zero-shot-classification", model="facebook/bart-large-mnli"
)


# Extract and preprocess text from transcripts.
def extract_text_from_vtt(vtt_path):
    transcript = []
    for caption in webvtt.read(vtt_path):
        transcript.append(caption.text)

    full_text = " ".join(transcript)
    return full_text


# Classify podcast transcript text.
def classify_text(text, candidate_labels):
    zero_shot_result = zero_shot_classifier(text, candidate_labels)

    # Extract the highest score label from each model's output.
    zero_shot_class = zero_shot_result["labels"][0]

    return zero_shot_class


# Process a directory of transcripts.
def process_vtt_directory(vtt_directory, candidate_labels):
    results = []
    files = [f for f in os.listdir(vtt_directory) if f.endswith(".vtt")]

    with alive_bar(len(files), title="Processing WebVTT Files") as bar:
        for filename in files:
            file_path = os.path.join(vtt_directory, filename)
            try:
                text = extract_text_from_vtt(file_path)
                zero_shot_class = classify_text(text, candidate_labels)
                results.append([filename, zero_shot_class])
            except Exception as e:
                print(f"Error processing {filename}: {e}")
            bar()

    # Return the results as a pandas DataFrame.
    return pd.DataFrame(results, columns=["filename", "zero shot classification"])


# Create the output spreadsheet.
def generate_spreadsheet(vtt_directory, output_file, candidate_labels):
    # Process the WebVTT directory and classify the transcripts.
    result_df = process_vtt_directory(vtt_directory, candidate_labels)

    # Save the results to a CSV file.
    result_df.to_csv(output_file, index=False)
    print(f"Classification results saved to {output_file}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process WebVTT files and classify their content."
    )
    parser.add_argument(
        "vtt_directory", type=str, help="Path to the directory containing VTT files."
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Path to the output CSV file where results will be saved.",
    )
    parser.add_argument(
        "--candidate-labels",
        type=str,
        required=True,
        help='Comma-separated list of candidate labels for classification, e.g., "label 1,label 2,label 3".',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    candidate_labels = [label.strip() for label in args.candidate_labels.split(",")]
    generate_spreadsheet(args.vtt_directory, args.output_file, candidate_labels)
