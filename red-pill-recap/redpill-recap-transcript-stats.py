import csv
import os
from collections import Counter

import nltk
import webvtt
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from transformers import AutoTokenizer

nltk.download("punkt")

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")


# Extract metrics from a transcript.
def extract_metrics(transcript):
    tokens = tokenizer.encode(transcript, truncation=False, add_special_tokens=False)
    token_count = len(tokens)
    word_count = len(transcript.split())
    char_count = len(transcript)
    sentences = sent_tokenize(transcript)
    sentence_count = len(sentences)
    avg_sentence_length = word_count / sentence_count if sentence_count else 0
    lexical_diversity = len(set(transcript.split())) / word_count if word_count else 0

    # Return the calculated metrics
    return {
        "token_count": token_count,
        "word_count": word_count,
        "char_count": char_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "lexical_diversity": lexical_diversity,
    }


# Extract text from a transcript file.
def extract_text_from_vtt(vtt_file_path):
    transcript = []
    try:
        for caption in webvtt.read(vtt_file_path):
            transcript.append(caption.text)
        return " ".join(transcript)
    except Exception as e:
        print(f"Error reading {vtt_file_path}: {e}")
        return ""


# Process transcript files.
def process_vtt_files(vtt_directory, output_csv_path):
    with open(output_csv_path, mode="w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "Filename",
                "Token Count",
                "Word Count",
                "Character Count",
                "Sentence Count",
                "Average Sentence Length",
                "Lexical Diversity",
            ]
        )

        vtt_files = [f for f in os.listdir(vtt_directory) if f.endswith(".vtt")]
        for vtt_file in tqdm(vtt_files, desc="Processing VTT files"):
            vtt_file_path = os.path.join(vtt_directory, vtt_file)
            transcript = extract_text_from_vtt(vtt_file_path)
            metrics = extract_metrics(transcript)

            csv_writer.writerow(
                [
                    vtt_file,
                    metrics["token_count"],
                    metrics["word_count"],
                    metrics["char_count"],
                    metrics["sentence_count"],
                    metrics["avg_sentence_length"],
                    metrics["lexical_diversity"],
                ]
            )

    print(f"\nData saved to {output_csv_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze VTT files and output metrics to CSV"
    )
    parser.add_argument("vtt_directory", type=str, help="Path to the VTT directory")
    parser.add_argument("output_csv_path", type=str, help="Path to save CSV output")
    args = parser.parse_args()
    process_vtt_files(args.vtt_directory, args.output_csv_path)
