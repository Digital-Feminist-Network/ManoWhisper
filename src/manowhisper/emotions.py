from alive_progress import alive_bar
from transformers import pipeline


def classify_emotions(sentences, model_pipeline):
    """Classifies emotions for each sentence."""
    emotion_scores = []
    with alive_bar(len(sentences), title="Classifying emotions") as bar:
        for sentence in sentences:
            result = model_pipeline(sentence)
            if isinstance(result, list) and isinstance(result[0], dict):
                emotion_dict = {
                    entry["label"].lower(): entry["score"] for entry in result
                }
                emotions = {
                    "anger": emotion_dict.get("anger", 0),
                    "disgust": emotion_dict.get("disgust", 0),
                    "fear": emotion_dict.get("fear", 0),
                    "joy": emotion_dict.get("joy", 0),
                    "neutral": emotion_dict.get("neutral", 0),
                    "sadness": emotion_dict.get("sadness", 0),
                    "surprise": emotion_dict.get("surprise", 0),
                }
                emotion_scores.append(emotions)
            else:
                print(f"Unexpected output for sentence: {sentence}")
                emotion_scores.append(
                    {
                        "anger": 0,
                        "disgust": 0,
                        "fear": 0,
                        "joy": 0,
                        "neutral": 0,
                        "sadness": 0,
                        "surprise": 0,
                    }
                )
            bar()

    return emotion_scores
