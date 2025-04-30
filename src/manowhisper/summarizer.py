import os

from alive_progress import alive_bar
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

from manowhisper import parser

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
model_name = "gmurro/bart-large-finetuned-filtered-spotify-podcast-summ"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, from_tf=True)


def split_text_into_chunks(text, max_tokens):
    """
    Split the transcript into manageable chunks.
    """
    input_ids = tokenizer(text, truncation=False, return_tensors="pt")["input_ids"][0]
    chunks = []
    for i in range(0, len(input_ids), max_tokens):
        chunk_ids = input_ids[i : i + max_tokens]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True)
        chunks.append(chunk_text)
    return chunks


def summarize_and_write(input_path, output_dir, max_input_length=2056):
    """
    Summarize WebVTT file(s) and write output.
    """
    # If input is a directory, process all WebVTT files in the directory
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

    # Process each WebVTT file.
    for vtt_file in vtt_files:
        fulltext = parser.extract_fulltext(vtt_file)
        chunks = split_text_into_chunks(fulltext, max_input_length - 50)
        concatenated_text = "\n".join(chunks)

        try:
            input_ids = summarizer.tokenizer(
                concatenated_text, truncation=False, return_tensors="pt"
            )["input_ids"]
            input_length = input_ids.shape[-1]

            if input_length < 50:
                raise ValueError(
                    f"Input too short for meaningful summarization: {input_length} tokens."
                )

            max_summary_length = min(input_length - 1, 512)

            summary = summarizer(
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
            print(f"Error during summarization: {str(e)}")
            summary = "Error generating summary."

        # Build output filename based on the original file name (with .txt extension).
        basename = os.path.basename(vtt_file)
        if basename.endswith(".vtt"):
            basename = basename[:-4]
        output_path = os.path.join(output_dir, f"{basename}.txt")

        # Ensure output directory exists.
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)
