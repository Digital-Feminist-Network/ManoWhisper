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
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet


def fetch_emotion_data(sheet):
    """
    Get emotion scores from a give Google Sheet with an assumed
    structure.
    """
    # Define the indexes for the emotion columns (from anger to surprise).
    emotion_indexes = [3, 4, 5, 6, 7, 8, 9]
    rows = sheet.get_all_values()
    emotion_data = []

    # Skip the header row
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

    return emotion_data


def plot_emotion_bar_chart(data, output_filename, title, script_name):
    """
    Generates an interactive bar chart representing the sum or average of emotion scores using Plotly.
    """
    episode_count = len(data)

    # Sum or average of scores for each emotion.
    emotion_sums = np.sum(data, axis=0)
    emotion_avgs = np.mean(data, axis=0)

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

    # Add sum trace to the primary y-axis (left side).
    fig.add_trace(
        go.Bar(
            x=emotions,
            y=emotion_sums,
            name="Sum of Scores",
            marker=dict(color="blue", opacity=0.7),
        ),
        # Primary y-axis (left side).
        secondary_y=False,
    )

    # Add average trace to the secondary y-axis (right side).
    fig.add_trace(
        go.Scatter(
            x=emotions,
            y=emotion_avgs,
            mode="lines+markers",
            name="Average Score",
            line=dict(color="red", width=4, dash="solid"),
            marker=dict(symbol="circle", size=8),
        ),
        secondary_y=True,
    )

    # Get the current timestamp for the footer.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = f"Generated: {timestamp}<br />Episode count: {episode_count}"

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
        height=1400,
        width=2560,
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

    # Save as HTML and static image.
    base_name, _ = os.path.splitext(output_filename)
    html_filename = base_name + ".html"
    fig.write_html(html_filename)

    print(f"Plot saved as {html_filename}")


@click.command()
@click.argument("google_sheet_id", type=str)
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
def main(google_sheet_id, output_filename, title, keyfile_path):
    """
    Generate an emotion bar chart from Google Sheets data.

    \b
    Arguments:
      GOOGLE_SHEET_ID   The ID of the Google Sheet.
      OUTPUT_FILENAME   Path to save the output chart image.
    """
    sheet = setup_google_sheets(google_sheet_id, keyfile_path)
    data = fetch_emotion_data(sheet)
    plot_emotion_bar_chart(
        data, output_filename, title, script_name="red-pill-emotional-damage.py"
    )


if __name__ == "__main__":
    main()
