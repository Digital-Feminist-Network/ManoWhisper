import glob
import os
import shlex
import subprocess

from alive_progress import alive_bar


def transcribe(
    input_path,
    threads,
    model="turbo",
    fp16="False",
    language="en",
    output_format="vtt",
):
    """
    Transcribe a media file or files in a directory using Whisper (cli).

    Args:
        input_path (str): Path to a file or directory containing media files.
        threads (int): Number of threads to use.
        model (str): Model to use for transcription. Default "turbo".
        fp16 (str): Whether to use fp16 precision. Default "False".
        language (str): Language to use. Default "en".
        output_format (str): Output file format. Default is "vtt".
    """
    if os.path.isdir(input_path):
        media_files = glob.glob(os.path.join(input_path, "*.m*"))
    elif os.path.isfile(input_path):
        media_files = [input_path]
    else:
        print(f"Invalid input path: {input_path}")
        return

    if not media_files:
        print(f"No media files found at {input_path}")
        return

    with alive_bar(len(media_files), title="Transcribing files") as bar:
        for media_file in media_files:
            quoted_file = shlex.quote(media_file)
            cmd_str = (
                f"CUDA_VISIBLE_DEVICES='' whisper --threads {threads} --model {model} "
                f"--fp16 {fp16} --language {language} {quoted_file} "
                f"--output_format {output_format}"
            )

            try:
                subprocess.run(cmd_str, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {media_file}: {e}")
                return

            bar()
