# ManoWhisper

A collection of utilities to transcribe, summarize, and classify a variety of Intellectual Dark Web, White Supremacist, and ManoSphere podcasts. These utilities came out of a research need for the [Digital Feminist Network](https://digfemnet.org/).

## About

### téléchargeur

Download a given podcast's episodes and descriptions.

* `python agloop.py --episodes "https://fight.fudgie.org/search/api/shows/sf/episodes" --transcripts vtt`
* `telechargeur configs/tucker.txt`

### les-observateurs

Watch a given podcast's media directory to detect new episodes and transcribe them with Whisper.

Examples:

* `python careless-whisper-pill.py "/home/ruestn/podcast-analysis/media/The Roseanne Barr Podcast/mp3"`
* `python les-observateurs.py configs/roseanne.toml`
* `python pill-feeder.py https://feeds.simplecast.com/vsy1m5LV`


### red-pill-bottles

Generate a variety of classifications based on transcripts or generated summaries.

Examples:

* `python EMOTIONAL-DAMAGE.py 1mjcwuaIJtW_9bGAebM3QK8RltWD9bKrjcr3qgMpivog`
* `python zero-shot-thirty.py --candidate-labels "gender,feminism,politics,religion" "/data/The Tucker Carlson Show/vtt" tucker-zero-shot.csv`

### red-pill-visions

Generate visualizations of a given podcast or all podcasts.

Examples:

* `python emotional-roller-coaster.py "Joe Rogan Experience #1509 - Abigail Shrier.vtt" "emotion-heatmap-joe-rogan-experience-1509-abigail-shrier.html" --title "Emotions: Joe Rogan Experience #1509 - Abigail Shrier"`
* `python red-pill-caliper.py "/data/The Culture War - Tim Pool/vtt" --podcast-name "The Culture War - Tim Pool"`
* `python red-pill-cloud.py "/data/The Culture War - Tim Pool/vtt"the-culture-war-podcast-with-tim-pool.png --width 2560 --height 1440 --title "The Culture War Podcast with Tim Pool" --additional-stopwords="think,know"`
* `python red-pill-emotional-damage.py 1LDz5LTeEuGhBOv3cSmlrysc9wswvIAKI_mRrrjQdydM emotions-the-ben-shapiro-show.png --title "Emotions of The Ben Shapiro Show (j-hartmann/emotion-english-distilroberta-base)"`
* `python red-pill-resonator.py --keywords "democrat*,republic*,deep state" --width 2560 --height 1440 --title "Keyword Trend: 'democrat*,republic*,deep state'" keyword-trend-democrat-republican-deep-state.html`

### red-pill-recap

Generate summarizations of a given podcast from a directory of transcript files.

Examples:

* `python recap-in-the-sheets.py "/data/The Joe Rogan Experience" 1mjcwuaIJtW_9bGAebM3QK8RltWD9bKrjcr3qgMpivog digfemnet.json`
* `python redpill-recap.py "/data/The Joe Rogan Experience/vtt" "/data/The Joe Rogan Experience/summarizations"`
* `python redpill-recap-stats.py "/data/The StoneZONE with Roger Stone/vtt/" roger-transcript-stats.csv`

## License

The Unlicense

## Acknowledgments

This project is part of the [Digital Feminist Network](https://digfemnet.org/) and is funded by the [Social Sciences and Humanities Research Council](https://www.sshrc-crsh.gc.ca/). Additional financial and in-kind support comes from [York University](https://www.yorku.ca/), [York University Libraries](https://www.library.yorku.ca/web/), the [Faculty of Arts](https://uwaterloo.ca/arts/), and the [David R. Cheriton School of Computer Science](https://cs.uwaterloo.ca/) at the [University of Waterloo](https://uwaterloo.ca/).
