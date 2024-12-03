"""
Generate emotion scores from podcast summaries in a Google Sheet.

Usage:
    EMOTIONAL-DAMAGE.py <google_sheet_id>

Arguments:
    sheet_id   Google sheet ID.
"""

import time
from collections import defaultdict

import gspread
from alive_progress import alive_bar
from oauth2client.service_account import ServiceAccountCredentials
from transformers import pipeline


# Setup function to connect to Google Sheets.
def setup_google_sheets(sheet_id, keyfile_path):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet


# Classify the emotion of the given summary using the provided model.
# Splits text into chunks if it exceeds the maximum length.
def classify_emotion(summary, model_pipeline, max_length=512):
    # Split summary into chunks of max_length.
    chunks = [summary[i : i + max_length] for i in range(0, len(summary), max_length)]

    aggregated_scores = defaultdict(float)

    for chunk in chunks:
        results = model_pipeline(chunk)

        # Aggregate scores across chunks.
        if isinstance(results, list) and isinstance(results[0], dict):
            for entry in results:
                aggregated_scores[entry["label"]] += entry["score"]
        else:
            print("Unexpected output structure from the model.")
            return {}

    # Average the scores over the number of chunks.
    num_chunks = len(chunks)
    return {label: score / num_chunks for label, score in aggregated_scores.items()}


def process_sheets(sheet_id, keyfile_path):
    sheet = setup_google_sheets(sheet_id, keyfile_path)

    # Load the "Summary" column; assume it's column 3.
    summaries = sheet.col_values(3)

    # Initialize the model pipeline.
    model_pipeline = pipeline(
        "text-classification", model="j-hartmann/emotion-english-distilroberta-base"
    )

    # Define emotion labels.
    emotion_labels = [
        "anger",
        "disgust",
        "fear",
        "joy",
        "neutral",
        "sadness",
        "surprise",
    ]

    # Get the headers.
    headers = sheet.row_values(1)

    # Find the first empty column.
    first_empty_col = len(headers) + 1

    # Add headers for emotion labels starting from the first empty column.
    for i, label in enumerate(emotion_labels):
        col_index = first_empty_col + i
        col_letter = chr(64 + col_index)
        sheet.update(range_name=f"{col_letter}1", values=[[label]])

    # Map emotion labels to column indices (starting from the first empty column).
    label_indices = {
        label: first_empty_col + i for i, label in enumerate(emotion_labels)
    }

    # Clear any existing emotion data in the columns (from second row onwards).
    range_to_clear = f"{chr(64 + first_empty_col)}2:{chr(64 + first_empty_col + len(emotion_labels) - 1)}"
    sheet.batch_clear([range_to_clear])

    # Loop through the summaries and classify each one.
    with alive_bar(len(summaries) - 1, title="Processing Summaries") as bar:
        for i, summary in enumerate(summaries[1:], start=2):

            # Get the emotion scores.
            emotion_scores = classify_emotion(summary, model_pipeline)

            # Prepare a row with the current data.
            row_update = []
            for label in emotion_labels:
                # Check if the label exists in emotion_scores, if not, use 0 as a default.
                emotion_score = emotion_scores.get(label, 0)
                row_update.append(round(emotion_score, 4))

            # Update the row with the emotion scores.
            range_to_update = f"{chr(64 + first_empty_col)}{i}:{chr(64 + first_empty_col + len(emotion_labels) - 1)}{i}"
            sheet.update(range_to_update, [row_update])

            # Add delay to avoid abusing the API.
            time.sleep(2)
            bar()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python EMOTIONAL-DAMAGE.py <google_sheet_id>")
        sys.exit(1)

    sheet_id = sys.argv[1]

    keyfile_path = "digfemnet-9b28b7e5668e.json"

    process_sheets(sheet_id, keyfile_path)
