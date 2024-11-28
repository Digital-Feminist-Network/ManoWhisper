"""
Downloads transcript files from fight.fudgie.org for a given show.

Usage:
    agloop.py --episodes <url> --transcripts <path/to/download/to>
    agloop.py --episodes "https://fight.fudgie.org/search/api/shows/jr/episodes" --transcripts vtt

Arguments:
    episodes       API endpoint for episodes
    transcripts    Directory to save transcripts
"""

import argparse
import os
import random
import time

import requests
from alive_progress import alive_bar


# Fetch episodes and get show ids.
def fetch_episodes(episodes_url):
    episodes = []
    while episodes_url:
        print(f"Fetching episodes from {episodes_url}...")
        response = requests.get(episodes_url)
        response.raise_for_status()
        data = response.json()

        episodes.extend(data["results"])
        episodes_url = data.get("next")
    return episodes


# Fetch the transcript for a given episode.
def fetch_transcript(episode_id, base_url):
    url = f"{base_url}/{episode_id}"
    print(f"Fetching transcript for {episode_id}...")
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# Write transcript in WebVTT format.
def write_transcript_vtt(transcript, title, output_path):
    vtt_filename = os.path.join(output_path, f"{title}.vtt")
    with open(vtt_filename, "w", encoding="utf-8") as vtt_file:
        vtt_file.write("WEBVTT\n\n")
        for entry in transcript:
            start = format_time(entry["start"])
            end = format_time(entry["end"])
            vtt_file.write(f"{start} --> {end}\n{entry['text']}\n\n")


# Format seconds to WebVTT time (hh:mm:ss.mmm).
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}".replace(".", ",")


def main(episodes_url, output_path):
    os.makedirs(output_path, exist_ok=True)

    # Fetch all episodes.
    episodes = fetch_episodes(episodes_url)

    with alive_bar(len(episodes), title="Downloading Transcripts") as bar:
        for episode in episodes:
            try:
                # Create sanitized file name for the episode.
                title = episode["title"].replace("/", "-")
                vtt_filename = os.path.join(output_path, f"{title}.vtt")

                # Check if the transcript already exists.
                if os.path.exists(vtt_filename):
                    print(f"Skipping {title}: already downloaded.")
                    bar()
                    continue

                # Fetch transcript data.
                episode_data = fetch_transcript(episode["id"], episodes_url)
                transcript = episode_data.get("transcript", [])

                # Write the transcript to a WebVTT file.
                write_transcript_vtt(transcript, title, output_path)

                # Random pause to be nice to fudgie.
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"Error processing {episode['id']}: {e}")
            bar()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download transcripts for episodes and save in WebVTT format."
    )
    parser.add_argument(
        "--episodes", type=str, required=True, help="API endpoint for episodes."
    )
    parser.add_argument(
        "--transcripts", type=str, required=True, help="Directory to save transcripts."
    )
    args = parser.parse_args()

    main(args.episodes, args.transcripts)
