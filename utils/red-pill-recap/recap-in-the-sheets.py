"""
Process directories of summaries and descriptions of a podcast to Google Sheets.

Usage:
    recap-in-the-sheets.py <podcast-directory> <google-sheet-id> <key.json>

Arguments:
    podcast_directory    Path to a podcast directory containaing a "summarizations" and a "descriptions" directory.
    google_sheet_id      A Google Sheet ID.
    key_file             Google API json key.
"""

import os
import sys
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Setup function to connect to Google Sheets.
def setup_google_sheets(sheet_id, keyfile_path):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1  # Assumes the first sheet.
    return sheet


# Process directories of summaries and descriptions.
def process_podcast(podcast_directory):
    summarizations_path = os.path.join(podcast_directory, "summarizations")
    descriptions_path = os.path.join(podcast_directory, "descriptions")

    # Ensure the required directories exist.
    if not os.path.isdir(summarizations_path) or not os.path.isdir(descriptions_path):
        raise FileNotFoundError(
            f"Expected directories 'summarizations' and 'descriptions' under {podcast_directory}."
        )

    episodes = []

    # Iterate through the summary files.
    for summary_file in os.listdir(summarizations_path):
        episode_name, ext = os.path.splitext(summary_file)
        if ext.lower() != ".txt":
            continue

        summary_path = os.path.join(summarizations_path, summary_file)
        description_file = f"{episode_name}.html"
        description_path = os.path.join(descriptions_path, description_file)

        # Read the summary.
        with open(summary_path, "r", encoding="utf-8") as s_file:
            summary_content = s_file.read()

        # Check for the description file; use an empty string if missing.
        if os.path.isfile(description_path):
            with open(description_path, "r", encoding="utf-8") as d_file:
                description_content = d_file.read()
        else:
            description_content = ""

        episodes.append(
            {
                "Episode": episode_name,
                "Description": description_content,
                "Summary": summary_content,
            }
        )

    return episodes


# Make sure headers exist.
def add_headers_if_missing(sheet):
    required_headers = ["Episode", "Description", "Summary"]
    existing_headers = sheet.row_values(1)

    # If the sheet is completely empty, add headers.
    if not existing_headers:
        sheet.insert_row(required_headers, 1)
    elif existing_headers != required_headers:
        # Validate and fix headers if necessary.
        for i, header in enumerate(required_headers):
            if i >= len(existing_headers) or existing_headers[i] != header:
                sheet.update_cell(1, i + 1, header)


# Check if an episode exists.
def episode_exists(sheet, episode_name):
    episodes = sheet.col_values(1)[1:]  # Skip the header
    return episode_name in episodes


# Append new episodes.
def append_to_sheet(sheet, episode):
    if not episode_exists(sheet, episode["Episode"]):
        sheet.append_row(
            [episode["Episode"], episode["Description"], episode["Summary"]]
        )
        time.sleep(1)


# Get all existing episode names.
def get_existing_episodes(sheet):
    # Epsisode names are in column 1.
    episodes = sheet.col_values(1)
    # Skip header row.
    return set(episodes[1:])


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python recap-in-the-sheets.py <podcast-directory> <google-sheet-id> <key.json>"
        )
        sys.exit(1)

    podcast_directory = sys.argv[1]
    google_sheet_id = sys.argv[2]
    key_file = sys.argv[3]

    # Connect to Google Sheets.
    sheet = setup_google_sheets(google_sheet_id, key_file)

    # Ensure headers are present.
    add_headers_if_missing(sheet)

    # Cache existing episodes.
    existing_episodes = get_existing_episodes(sheet)

    # Parse the podcast directory.
    episodes = process_podcast(podcast_directory)

    # Append episodes to the sheet.
    for episode in episodes:
        if episode["Episode"] not in existing_episodes:
            append_to_sheet(sheet, episode)
            # Add to cache.
            existing_episodes.add(episode["Episode"])


if __name__ == "__main__":
    main()
