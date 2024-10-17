import glob
import os
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: python careless-whisper-pill.py <directory_path>")
    sys.exit(1)

directory_path = sys.argv[1]

model = "turbo"
threads = 24
fp16 = "False"
language = "en"
output_format = "vtt"

mp3_files = glob.glob(os.path.join(directory_path, "*.mp3"))

def process_file(mp3_file):
    output_dir = os.path.dirname(mp3_file)

    cmd_str = (
        f"whisper --threads {threads} --model {model} "
        f"--fp16 {fp16} --language {language} \"{mp3_file}\" "
        f"--output_format {output_format} --output_dir \"{output_dir}\""
    )

    try:
        subprocess.run(cmd_str, shell=True, check=True)
        print(f"Successfully processed {mp3_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {mp3_file}: {e}")

for mp3_file in mp3_files:
    process_file(mp3_file)

print("Processing completed.")
