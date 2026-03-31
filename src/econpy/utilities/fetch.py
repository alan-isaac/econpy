"""
Download and extract files from URLs.

Example use (given `myfiles`, a list or URLs)::
    hmpth = pathlib.Path("/temp/myFolder")
    dlFolder = hmpth / "download"
    exFolder = hmpth / "extract"
    fetchZipContents(myfiles, zipDir=dlFolder, tgtDir=exFolder)
"""

import os
import requests
import zipfile
import pathlib
from urllib.parse import urlparse


def fetchFile(
    url: list[str],             # file URL (e.g., a .zip file URL)
    saveFolder: str|pathlib.Path  # Directory to save downloaded files.
    ) -> pathlib.Path:  # the location of the saved file
    """
    Download multiple files from a list of URLs.
    """
    # Extract filename from URL
    filename = os.path.basename(urlparse(url).path)
    tgtPath = pathlib.Path(saveFolder, filename)
    print(f"↓ Downloading: {filename} to {tgtPath}")
    try: # Stream download to handle large files
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0

            with open(tgtPath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.2f}%", end="")

        print(f"\n✅ Saved to: {tgtPath}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
    except Exception as e:
        print(f"⚠ Unexpected error for {url}: {e}")
    return tgtPath

def fetchFiles(
    urls: list[str],                # file URLs (e.g., .zip file URLs)
    saveFolder: str|pathlib.Path    # Directory to save downloaded files.
    ) -> None:
    """
    Download multiple files from a list of URLs.
    """
    os.makedirs(saveFolder, exist_ok=True)
    fpaths = list()
    for url in url_list:
        fpath = fetchFile(url, saveFolder)
        fpaths.append(fpath)

def extractZip(
    zipPath: str|pathlib.Path,  # path to .zip file
    tgtFolder: str|pathlib.Path # folder for extracted files
    ) -> None:
    ext = pathlib.Path(zipPath).suffix
    if not ext.lower() == ".zip"
        print(f"❌ Abort extraction: unexpected file type: {zipPath}")
    else: # Extract the ZIP file
        print(f"📦 Attempt extraction of {filename} …")
        try:
            with zipfile.ZipFile(zipPath, 'r') as zip_ref:
                zip_ref.extractall(tgtFolder)
            print(f"✅ Extracted to: {tgtFolder}")
        except zipfile.BadZipFile:
            print(f"❌ Error: {zipPath} is not a valid ZIP file.")

def fetchZipContents(
    urls: list[str],           # .zip file URLs
    zipDir: str|pathlib.Path,  # folder for dowloaded .zip files
    tgtDir: str|pathlib.Path   # where to extract the .zip files
    ) -> None:
    """
    Download .zip files from a list of URLs and extract them.
    Comment: the zip files are retained in their folder.
    """
    zpaths: list[pathlib.Path] = fetchFiles(urls, zipDir)

    os.makedirs(tgtDir, exist_ok=True)
    for zpath in zpaths:
        extractZip(zpath, tgtDir)



