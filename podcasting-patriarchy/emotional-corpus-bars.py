import gspread
import pandas as pd
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
from plotly.subplots import make_subplots

emotion_colors = {
    "anger": "#a4161a",
    "disgust": "#9d4edd",
    "fear": "#d58936",
    "joy": "#ffd100",
    "neutral": "#f5f3f4",
    "sadness": "#3066be",
    "surprise": "#90be6d",
}


def setup_google_sheets(sheet_id, keyfile_path):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)


def get_mean_emotions(sheet):
    data = pd.DataFrame(sheet.get_all_records())
    return data.mean(numeric_only=True)


def generate_custom_emotion_facets(
    sheet_id, keyfile_path, gids, titles, output_html, overall_title
):
    if len(gids) != len(titles):
        raise ValueError("Each GID must have a corresponding title.")

    doc = setup_google_sheets(sheet_id, keyfile_path)

    fig = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=titles,
        horizontal_spacing=0.1,
        vertical_spacing=0.2,
    )

    for i, (gid, title) in enumerate(zip(gids, titles)):
        sheet = doc.get_worksheet_by_id(int(gid))
        mean_scores = get_mean_emotions(sheet)

        row = i // 3 + 1
        col = i % 3 + 1

        fig.add_trace(
            go.Bar(
                x=mean_scores.index,
                y=mean_scores.values,
                marker_color=[
                    emotion_colors.get(emotion, "#000000")
                    for emotion in mean_scores.index
                ],
                name=title,
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        title=dict(text=overall_title, x=0.5, font=dict(size=26)),
        height=800,
        showlegend=False,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
        ),
    )

    fig.write_html(output_html)
    print(f"Saved to {output_html}")


if __name__ == "__main__":
    sheet_id = "120larZoQGBKuHIqCUaS7B4UIBYk_7YYjLi26il1AN4Y"
    keyfile_path = "digfemnet-9b28b7e5668e.json"
    gids = [0, 1306925960, 208777064, 1522008939, 1748617768]
    titles = [
        "America First - Nicholas J. Fuentes",
        "Tate Speech",
        "Candace Owens",
        "The Tucker Carlson Show",
        "Get Off My Lawn - Gavin McInnes",
    ]
    output_html = "emotion-facets.html"
    overall_title = "Mean Emotion Prevalence Classification"

    generate_custom_emotion_facets(
        sheet_id, keyfile_path, gids, titles, output_html, overall_title
    )
