"""
Generates summaries from a directory of WebVTT files..

Usage:
    redpill-recap.py "/path/to/vtt" "/path/to/summarizations"

Arguments:
    vtt_directory       Directory of WebVTT files
    output_directory    Directory to save summarizations
"""

import os

import webvtt
from alive_progress import alive_bar
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# Load model and tokenizer with TensorFlow weights.
model_name = "gmurro/bart-large-finetuned-filtered-spotify-podcast-summ"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, from_tf=True)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# Define a maximum chunk size based on the model's limit.
MAX_INPUT_TOKENS = 1024


# Extract and preprocess text from transcripts.
def extract_text_from_vtt(vtt_file_path):
    transcript = []
    for caption in webvtt.read(vtt_file_path):
        transcript.append(caption.text)
    full_text = " ".join(transcript)
    return full_text


# Split the transcript into manageable chunks.
def split_text_into_chunks(text, max_tokens):
    input_ids = tokenizer(text, truncation=False, return_tensors="pt")["input_ids"][0]
    chunks = []
    for i in range(0, len(input_ids), max_tokens):
        chunk_ids = input_ids[i : i + max_tokens]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunks.append(chunk_text)
    return chunks


# Summarize a preprocessed transcript and write the result.
def summarize_and_write(vtt_file_path, output_file_path, max_input_length=1024):
    transcript = extract_text_from_vtt(vtt_file_path)
    # Split the transcript into smaller, overlapping chunks.
    chunks = split_text_into_chunks(transcript, max_input_length - 50)
    concatenated_text = "\n".join(chunks)

    try:
        # Tokenize the concatenated text to determine input length.
        input_ids = tokenizer(concatenated_text, truncation=False, return_tensors="pt")[
            "input_ids"
        ]
        input_length = input_ids.shape[-1]

        # Ensure max_length is less than input_length for summarization.
        if input_length < 50:
            raise ValueError(
                f"Input too short for meaningful summarization: {input_length} tokens."
            )

        # Dynamically adjust max_summary_length to fit the input length.
        max_summary_length = min(
            input_length - 1, 512
        )  # Ensure max_length < input_length

        final_summary = summarizer(
            concatenated_text,
            truncation=True,
            max_length=max_summary_length,
            min_length=min(50, max_summary_length // 2),
            no_repeat_ngram_size=3,
            early_stopping=True,
            num_beams=5,
            length_penalty=1.0,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            do_sample=True,
        )[0]["summary_text"]

    except Exception as e:
        print(f"Error during final summarization for {vtt_file_path}: {str(e)}")
        final_summary = "Error generating summary."

    # Write the summary to file.
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(final_summary)

    print(
        f"Saved single summary for {os.path.basename(vtt_file_path)} to {output_file_path}"
    )


# Process a directory of transcripts with a progress bar.
def process_vtt_directory(vtt_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    vtt_files = [f for f in os.listdir(vtt_directory) if f.endswith(".vtt")]

    with alive_bar(len(vtt_files), title="Processing WebVTT files", unit="file") as bar:
        for filename in vtt_files:
            vtt_file_path = os.path.join(vtt_directory, filename)
            base_filename = os.path.splitext(filename)[0]
            output_file_path = os.path.join(output_directory, f"{base_filename}.txt")

            # Skip already processed files.
            if os.path.exists(output_file_path):
                print(f"Summary already exists for {filename}, skipping...")
                bar()
                continue

            summarize_and_write(vtt_file_path, output_file_path)
            bar()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process WebVTT files and summarize their content."
    )
    parser.add_argument(
        "vtt_directory", type=str, help="Path to the directory containing WebVTT files"
    )
    parser.add_argument(
        "output_directory", type=str, help="Path to the directory to save summaries"
    )

    args = parser.parse_args()
    process_vtt_directory(args.vtt_directory, args.output_directory)
