import os
import random
import time

import click
import gspread
import spacy
import webvtt
from alive_progress import alive_bar
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError


def setup_google_sheets(json_keyfile):
    """Setup function to connect to Google Sheets."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(json_keyfile, scopes=scope)
    client = gspread.authorize(credentials)
    return client


def extract_text_from_vtt(vtt_path):
    """Extract and preprocess text from transcripts."""
    return " ".join(caption.text for caption in webvtt.read(vtt_path))


def retry_on_quota_error(func, *args, max_retries=5, base_delay=2, **kwargs):
    """
    Retry the given function on quota errors with exponential backoff.
    """
    retries = 0
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except APIError as e:
            if "Quota exceeded" in str(e):
                retries += 1
                delay = base_delay * (2**retries) + random.uniform(0, 1)
                print(
                    f"Quota exceeded. Retrying in {delay:.2f} seconds... (Attempt {retries}/{max_retries})"
                )
                time.sleep(delay)
            else:
                raise
    raise Exception("Maximum retries reached for Google Sheets API request.")


def process_vtt_files(vtt_directory, json_keyfile, spreadsheet_id):
    """
    Extract "PERSON", "NORP", "FAC", "ORG", and "PRODUCT" from transcripts.
    """

    # Load spaCy model.
    nlp = spacy.load("en_core_web_sm")

    # Set up Google Sheets.
    client = setup_google_sheets(json_keyfile)
    spreadsheet = retry_on_quota_error(client.open_by_key, spreadsheet_id)
    worksheet = retry_on_quota_error(spreadsheet.worksheet, "ner")

    # Check if headers already exist.
    existing_headers = retry_on_quota_error(worksheet.row_values, 1)
    headers = ["Filename", "PERSON", "NORP", "FAC", "ORG", "PRODUCT"]
    if headers != existing_headers:
        retry_on_quota_error(worksheet.insert_row, headers, 1)

    # Get list of WebVTT files.
    vtt_files = [f for f in os.listdir(vtt_directory) if f.endswith(".vtt")]

    # Retrieve filenames already in the worksheet.
    existing_filenames = retry_on_quota_error(worksheet.col_values, 1)

    # Iterate through transcripts and extract entities.
    with alive_bar(len(vtt_files), title="Processing VTT files") as bar:
        for filename in vtt_files:
            if filename in existing_filenames:
                print(f"Skipping {filename}, already processed.")
                bar()
                continue

            vtt_path = os.path.join(vtt_directory, filename)

            processed_content = extract_text_from_vtt(vtt_path)
            doc = nlp(processed_content)
            entities = {"PERSON": [], "NORP": [], "FAC": [], "ORG": [], "PRODUCT": []}

            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)

            # Prep data for the Google Sheet.
            row = [
                filename,
                "|".join(set(entities["PERSON"])),
                "|".join(set(entities["NORP"])),
                "|".join(set(entities["FAC"])),
                "|".join(set(entities["ORG"])),
                "|".join(set(entities["PRODUCT"])),
            ]

            # Check if the filename already exists in the worksheet.
            retry_on_quota_error(worksheet.append_row, row)
            time.sleep(1)
            bar()


@click.command()
@click.argument("vtt_directory", type=click.Path(exists=True, file_okay=False))
@click.argument("json_keyfile", type=click.Path(exists=True, dir_okay=False))
@click.argument("spreadsheet_id", type=str)
def main(vtt_directory, json_keyfile, spreadsheet_id):
    """
    Process a directory of WebVTT files and extract entities using spaCy. Write
    the output to a Google Sheet.
    """
    process_vtt_files(vtt_directory, json_keyfile, spreadsheet_id)


if __name__ == "__main__":
    main()
