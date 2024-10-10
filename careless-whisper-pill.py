import glob
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

if len(sys.argv) != 2:
    print("Usage: python careless-whisper-pill.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]

# Assumes whisper.cpp is here.
project_path = "/home/ruestn/podcast-analysis"

# Use only the ggml-large-v3 model
model = "ggml-large-v3"

wav_files = glob.glob(os.path.join(directory_path, "*.wav"))

# Dynamic thread allocation.
cpu_cores = os.cpu_count()
thread_count = min(6, cpu_cores)


def process_file(wav_file):
    base_filename = os.path.splitext(os.path.basename(wav_file))[0]
    iso = "en"

    vtt_file_path = os.path.join(directory_path, f"{base_filename}.{model}.wav.vtt")
    if os.path.isfile(vtt_file_path):
        return f"VTT file already exists for {base_filename}, skipping."

    model_path = os.path.join(project_path, f"whisper.cpp/models/{model}.bin")
    if not os.path.isfile(model_path):
        return f"Model file does not exist: {model_path}"

    cmd_str = (
        f"{project_path}/whisper.cpp/main "
        f"-m {model_path} "
        f'--output-vtt -l {iso} -f "{wav_file}" -t {thread_count}'
    )

    try:
        subprocess.run(cmd_str, shell=True, check=True)

        output_vtt_path = f"{wav_file}.{model}.vtt"
        if os.path.isfile(output_vtt_path):
            shutil.move(output_vtt_path, vtt_file_path)
        else:
            return f"Failed to find generated VTT for {wav_file} with model {model}"
    except subprocess.CalledProcessError as e:
        return f"Error processing {wav_file} with model {model}: {e}"

    return f"Successfully processed {wav_file}"


# Progress tracker.
total_files = len(wav_files)

# Parallel processing.
with ThreadPoolExecutor(max_workers=4) as executor:
    with tqdm(total=total_files, desc="Processing WAV files", unit="file") as pbar:
        futures = []
        for wav_file in wav_files:
            futures.append(executor.submit(process_file, wav_file))

        for future in futures:
            result = future.result()
            pbar.update(1)
            print(result)

print("Processing completed.")
