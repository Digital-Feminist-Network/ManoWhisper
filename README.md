# ManoWhisper

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15287350.svg)](https://doi.org/10.5281/zenodo.15287350)

`manowhisper`: Command line utility for transcribing, summarizing, classifying, and creating visualizations of WebVTT files.

`utils`: A collection of utilities for transcribing, summarizing, classifying, and creating visualizations from transcripts and summaries of various podcasts associated with the Intellectual Dark Web, conspiracy theories, QAnon, the Alt-Right, White Supremacist/Nationalist movements, and the Manosphere.


## Installation

```
pip install manowhisper
```

## Usage

```
Usage: manowhisper [OPTIONS] COMMAND [ARGS]...

  manowhisper - transcribing, summarize, classify, and create visualizations
  of WebVTT files.

Options:
  --help  Show this message and exit.

Commands:
  classify    Classify WebVTT files.
  emotions    Classify emotions in WebVTT files.
  transcribe  Transcribe audio files.
```

### Classify

```
usage: manowhisper classify [OPTIONS] OUTPUT

  Classify WebVTT files.

Options:
  --model [transphobia|sexism|hate|misogyny]
                                  Model to use for classification.  [required]
  --input PATH                    Path to input files.  [required]
  --help                          Show this message and exit.
```

### Emotions

```
Usage: manowhisper emotions [OPTIONS] OUTPUT

  Classify emotions in WebVTT files.

Options:
  --input PATH  Path to input files.  [required]
  --help        Show this message and exit.
```

### Summarize

```
Usage: manowhisper summarize [OPTIONS]

  Summarize WebVTT files.

Options:
  --input PATH            Path to input VTT file or directory.  [required]
  --output-dir DIRECTORY  Directory to save summaries.  [required]
  --help                  Show this message and exit.
```

### Transcribe

```
Usage: manowhisper transcribe [OPTIONS]

  Transcribe audio files.

Options:
  --threads INTEGER     Number of threads to use.  [required]
  --model TEXT          Model to use for transcription. Default is 'turbo'.
  --fp16 BOOLEAN        Whether to use fp16 precision. Default is False.
  --language TEXT       Language of the audio. Default is 'en'.
  --output_format TEXT  Output format. Default is 'vtt'.
  --input PATH          Path to input files (directory or single file).
                        [required]
  --help                Show this message and exit.
```

## License

The Unlicense

## Acknowledgments

This project is part of the [Digital Feminist Network](https://digfemnet.org/) and is funded by the [Social Sciences and Humanities Research Council](https://www.sshrc-crsh.gc.ca/). Additional financial and in-kind support comes from [York University](https://www.yorku.ca/), [York University Libraries](https://www.library.yorku.ca/web/), the [Faculty of Arts](https://uwaterloo.ca/arts/), and the [David R. Cheriton School of Computer Science](https://cs.uwaterloo.ca/) at the [University of Waterloo](https://uwaterloo.ca/).
