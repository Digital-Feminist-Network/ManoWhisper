# ManoWhisper

A collection of utilities for transcribing, summarizing, classifying, and creating visualizations from transcripts and summaries of various podcasts associated with the Intellectual Dark Web, conspiracy theories, QAnon, the Alt-Right, White Supremacist/Nationalist movements, and the Manosphere.

## About

### téléchargeur

Download a given podcast's episodes and descriptions, or fetch transcripts from an API.

Examples:

 ```shell
python agloop.py --episodes "https://fight.fudgie.org/search/api/shows/sf/episodes" --transcripts vtt
```

```shell
python pill-feeder.py https://feeds.simplecast.com/vsy1m5LV
```

```bash
telechargeur configs/tucker.txt
```

### les-observateurs

Watch a given podcast's media directory to detect new episodes and transcribe them with Whisper.

Examples:

```shell
python careless-whisper-pill.py "/data/The Roseanne Barr Podcast/mp3"
```

```shell
python les-observateurs.py configs/roseanne.toml
```

### red-pill-bottles

Generate a variety of classifications based on transcripts or generated summaries.

Examples:

```shell
python EMOTIONAL-DAMAGE.py 1mjcwuaIJtW_9bGAebM3QK8RltWD9bKrjcr3qgMpivog
```

```shell
python zero-shot-thirty.py --candidate-labels "gender,feminism,politics,religion" "/data/The Tucker Carlson Show/vtt" tucker-zero-shot.csv
```

### red-pill-visions

Generate [visualizations](https://ruebot.net/visualizations/mano-whisper/) from the transcripts or summaries of one or more podcasts.

Examples:

```shell
python emotional-roller-coaster.py "Joe Rogan Experience #1509 - Abigail Shrier.vtt" "emotion-heatmap-joe-rogan-experience-1509-abigail-shrier.html" --title "Emotions: Joe Rogan Experience #1509 - Abigail Shrier"
```

```shell
python red-pill-caliper.py "/data/The Culture War - Tim Pool/vtt" --podcast-name "The Culture War - Tim Pool"
```

```shell
python red-pill-cloud.py "/data/The Culture War - Tim Pool/vtt"the-culture-war-podcast-with-tim-pool.png --width 2560 --height 1440 --title "The Culture War Podcast with Tim Pool" --additional-stopwords="think,know"
```

```shell
python red-pill-emotional-damage.py 1oIa4jk5DagHvqpclM3j5kkK2dagG3FL42VRL5n3jIdM 1HJYZPfOoChrlvv9TyeZib74au-RMDciHI6TKB9gTiks emotions-matt-gaetz-donald-trump-jr.html --title "Emotions of Triggered - Donald Trump Jr & Firebrand - Matt Gaetz (j-hartmann/emotion-english-distilroberta-base)"
```

```shell
python red-pill-resonator.py --keywords "democrat*,republic*,deep state" --width 2560 --height 1440 --title "Keyword Trend: 'democrat*,republic*,deep state'" keyword-trend-democrat-republican-deep-state.html
```

```shell
python wave-of-misogyny.py "/data/Fresh & Fit/vtt/NFL Player Speech Valid or Misogynistic?.vtt" "misogyny-wave-nfl-player-speech-valid-or-misogynistic.html" --title "Fresh & Fit: NFL Player Speech Valid or Misogynistic? (MilaNLProc/bert-base-uncased-ear-misogyny)"
```

### red-pill-recap

Generate summarizations of a given podcast from a directory of transcript files.

Examples:

```shell
python recap-in-the-sheets.py "/data/The Joe Rogan Experience" 1mjcwuaIJtW_9bGAebM3QK8RltWD9bKrjcr3qgMpivog digfemnet.json
```

```shell
python redpill-recap.py "/data/The Joe Rogan Experience/vtt" "/data/The Joe Rogan Experience/summarizations"
```

```shell
python redpill-recap-stats.py "/data/The StoneZONE with Roger Stone/vtt/" roger-transcript-stats.csv
```

## License

The Unlicense

## Acknowledgments

This project is part of the [Digital Feminist Network](https://digfemnet.org/) and is funded by the [Social Sciences and Humanities Research Council](https://www.sshrc-crsh.gc.ca/). Additional financial and in-kind support comes from [York University](https://www.yorku.ca/), [York University Libraries](https://www.library.yorku.ca/web/), the [Faculty of Arts](https://uwaterloo.ca/arts/), and the [David R. Cheriton School of Computer Science](https://cs.uwaterloo.ca/) at the [University of Waterloo](https://uwaterloo.ca/).
