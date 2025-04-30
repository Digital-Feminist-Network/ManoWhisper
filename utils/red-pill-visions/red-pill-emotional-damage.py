import os
from datetime import datetime

import click
import gspread
import numpy as np
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from plotly.subplots import make_subplots


def setup_google_sheets(sheet_id, keyfile_path):
    """
    Setup function to connect to Google Sheets.
    """
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    return sheet


def fetch_emotion_data(sheet):
    """
    Get emotion scores from all worksheets in a Google Sheet.

    Makes assumptions on how the spreadsheet is laid out.

    Header row:
    Episode,Description,Summary,anger,disgust,fear,joy,neutral,sadness,surprise.
    """
    emotion_indexes = [3, 4, 5, 6, 7, 8, 9]
    worksheets_data = []
    total_episode_count = 0

    for worksheet in sheet.worksheets():
        rows = worksheet.get_all_values()
        emotion_data = []

        # Skip the header row.
        header = rows[0]
        if header[0].lower() == "episode":
            rows = rows[1:]

        for row in rows:
            if len(row) >= len(emotion_indexes) + 3:
                try:
                    emotion_data.append(
                        [float(row[i]) if row[i] else 0 for i in emotion_indexes]
                    )
                except ValueError:
                    print(f"Skipping row due to conversion error: {row}")
            else:
                print(f"Skipping incomplete row: {row}")

        if emotion_data:
            worksheets_data.append((worksheet.title, emotion_data))
            total_episode_count += len(emotion_data)

    return worksheets_data, total_episode_count


def fetch_spreadsheet_title(sheet):
    """
    Retrieve the title of the spreadsheet.
    """
    return sheet.title


def plot_emotion_bar_chart(data, total_episode_count, output_filename, title):
    """
    Generates an interactive bar chart overlaying emotion scores across worksheets.
    """
    emotions = [
        "Anger 🤬",
        "Disgust 🤢",
        "Fear 😨",
        "Joy 😀",
        "Neutral 😐",
        "Sadness 😭",
        "Surprise 😲",
    ]

    # Create a figure with a secondary y-axis.
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot data for each worksheet.
    for sheet_title, worksheet_title, emotion_data in data:
        emotion_sums = np.sum(emotion_data, axis=0)
        emotion_avgs = np.mean(emotion_data, axis=0)

        # Add sum trace to the primary y-axis (left side).
        fig.add_trace(
            go.Bar(
                x=emotions,
                y=emotion_sums,
                name=f"{sheet_title} (Sum)",
                marker=dict(opacity=0.7),
            ),
            secondary_y=False,
        )

        # Add average trace to the secondary y-axis (right side).
        fig.add_trace(
            go.Scatter(
                x=emotions,
                y=emotion_avgs,
                mode="lines+markers",
                name=f"{sheet_title} (Avg)",
                line=dict(width=2),
                marker=dict(symbol="circle", size=8),
            ),
            secondary_y=True,
        )

    # Get the current timestamp for the footer.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = (
        f"Generated: {timestamp}<br />Total episode count: {total_episode_count}"
    )

    # Update layout.
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=35, family="Arial", weight="bold"),
        },
        xaxis=dict(
            title="Emotion",
            title_font=dict(size=18, family="Arial", weight="bold"),
            tickangle=45,
            tickmode="array",
            tickvals=emotions,
            tickfont=dict(size=16, family="Arial", weight="bold"),
        ),
        yaxis=dict(
            title="Sum of Scores",
            title_font=dict(size=18, family="Arial", weight="bold"),
            tickfont=dict(size=16, family="Arial", weight="bold"),
        ),
        yaxis2=dict(
            title="Average Score",
            title_font=dict(size=18, family="Arial", weight="bold"),
            tickfont=dict(size=16, family="Arial", weight="bold"),
            overlaying="y",
            side="right",
            range=[0, 1],
        ),
        showlegend=True,
        margin=dict(l=50, r=50, t=100, b=100),
        height=1237.5,
        width=2200,
        annotations=[
            {
                "x": 1,
                "y": -0.1,
                "xref": "paper",
                "yref": "paper",
                "text": footer_text,
                "showarrow": False,
                "font": dict(size=12, color="gray"),
                "align": "right",
            }
        ],
    )

    # Save as HTML.
    base_name, _ = os.path.splitext(output_filename)
    html_filename = base_name + ".html"
    fig.write_html(html_filename)

    print(f"Plot saved as {html_filename}")


@click.command()
@click.argument("google_sheet_ids", type=str, nargs=-1)
@click.argument("output_filename", type=str)
@click.option(
    "--title",
    type=str,
    default="Emotion Bar Chart",
    show_default=True,
    help="Title for the graph.",
)
@click.option(
    "--keyfile-path",
    type=click.Path(exists=True),
    default="digfemnet-9b28b7e5668e.json",
    show_default=True,
    help="Path to the JSON key file for Google Sheets API authentication.",
)
def main(google_sheet_ids, output_filename, title, keyfile_path):
    """
    Generate an emotion bar chart from multiple Google Sheets.

    \b
    Arguments:
      GOOGLE_SHEET_IDS   Space-separated IDs of the Google Sheets.
      OUTPUT_FILENAME    Path to save the output chart image.
    """
    all_data = []
    total_episode_count = 0

    for sheet_id in google_sheet_ids:
        sheet = setup_google_sheets(sheet_id, keyfile_path)
        sheet_title = fetch_spreadsheet_title(sheet)
        worksheet_data, episode_count = fetch_emotion_data(sheet)
        for worksheet_title, emotion_data in worksheet_data:
            all_data.append((sheet_title, worksheet_title, emotion_data))
        total_episode_count += episode_count

    plot_emotion_bar_chart(all_data, total_episode_count, output_filename, title)


if __name__ == "__main__":
    main()
