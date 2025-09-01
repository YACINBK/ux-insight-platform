#!/usr/bin/env python3
import os
import pathlib
import urllib.request
import zipfile

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
print(f"Data dir: {DATA_DIR}")
# TODO: add URLs for small demo assets
print("Fetch datasets: add URLs and unzip here.")