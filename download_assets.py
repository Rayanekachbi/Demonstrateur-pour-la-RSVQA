import os

# use this command to install gdown if you don't have it
# pip install gdown
# To run this script, use the command:
# python download_assets.py

import gdown

# === CONFIGURATION ===
DOWNLOADS = {
    "BigModel_30.tar": "https://drive.google.com/uc?id=101gGRQi0eRU0WdjbIqmYk8jaHy1S4tbv",
    "datasets/High_Resolution/all_questions.json": "https://drive.google.com/uc?id=1nOYw0tQVoX93ECexSUUjdhALUgrj4XZF",
    "datasets/High_Resolution/all_answers.json": "https://drive.google.com/uc?id=1Nl11RF5eTfLqSPba8uGL8W_wKSGowTU5",
    "datasets/High_Resolution/USGS_split_train_questions.json": "https://drive.google.com/uc?id=1HbxsP2JjGCIY6tgmbwb3LKJEvwQPOCrm"
}

def download_file(dest_path, url):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path):
        print(f"✅ Already exists: {dest_path}")
        return
    print(f"⬇️ Downloading from Google Drive: {dest_path}")
    gdown.download(url, dest_path, quiet=False)

if __name__ == "__main__":
    for dest, url in DOWNLOADS.items():
        download_file(dest, url)
