# download_ghibli_model.py

from huggingface_hub import hf_hub_download
import os

# Replace this with your actual token
HF_TOKEN = "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"

# The repository and filename
REPO_ID = "nitrosocke/Ghibli-Diffusion"
FILENAME = "ghibli-diffusion-v1.ckpt"


# Download the file
downloaded_file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    token=HF_TOKEN
)

print(f"Model downloaded to: {downloaded_file_path}")
