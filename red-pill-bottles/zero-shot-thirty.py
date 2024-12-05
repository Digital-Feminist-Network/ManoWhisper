import os

import click
import pandas as pd
import webvtt
from alive_progress import alive_bar
from transformers import pipeline

# Initialize the zero-shot classification pipeline.
zero_shot_classifier = pipeline(
    "zero-shot-classification", model="facebook/bart-large-mnli"
)


def extract_text_from_vtt(vtt_path):
    """Extract and preprocess text from transcripts."""
    transcript = []
    for caption in webvtt.read(vtt_path):
        transcript.append(caption.text)
    return " ".join(transcript)


def classify_text(text, candidate_labels):
    """Classify podcast transcript text."""
    zero_shot_result = zero_shot_classifier(text, candidate_labels)
    return zero_shot_result["labels"][0]  # Highest score label


def process_vtt_directory(vtt_directory, candidate_labels):
    """Process a directory of transcripts."""
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
    return pd.DataFrame(results, columns=["filename", "zero_shot_classification"])


def generate_spreadsheet(vtt_directory, output_file, candidate_labels):
    """Create the output spreadsheet."""
    result_df = process_vtt_directory(vtt_directory, candidate_labels)
    result_df.to_csv(output_file, index=False)
    print(f"Classification results saved to {output_file}")


@click.command()
@click.argument("vtt_directory", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--candidate-labels",
    type=str,
    required=True,
    help="Comma-separated list of candidate labels for classification, e.g., 'label 1,label 2,label 3'.",
)
def main(vtt_directory, output_file, candidate_labels):
    """
    Process a directory of WebVTT files and do zero-shot classification content with facebook/bart-large-mnli.

    \b
    Arguments:
      VTT_DIRECTORY   Path to the directory containing WebVTT files.
      OUTPUT_FILE     Path to the output CSV file where results will be saved.

    \b
    Options:
      --candidate-labels   Comma-separated list of candidate labels for classification.
    """
    # Split and clean candidate labels.
    candidate_labels_list = [label.strip() for label in candidate_labels.split(",")]
    generate_spreadsheet(vtt_directory, output_file, candidate_labels_list)


if __name__ == "__main__":
    main()
