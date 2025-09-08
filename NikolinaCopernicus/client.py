import os
import requests
import spypoint
from urllib.parse import urlparse

class Cleaner:
    @staticmethod
    def clean_filename(url):
        url_parsed=urlparse(url)
        return os.path.basename(url_parsed.path)

class Loader:
    def __init__(self):
        self.USERNAME = "andreas.senn@copernitech.com"
        self.PASSWORD = "823-fweJäfwef3D"
        self.LOCAL_FOLDER = "spypoint_images"
        os.makedirs(self.LOCAL_FOLDER, exist_ok=True)
        c = spypoint.Client(self.USERNAME, self.PASSWORD)
        cams = c.cameras()
        for photo in c.photos(cams):
            url = photo.url()
            filename = os.path.join(self.LOCAL_FOLDER, Cleaner.clean_filename(url))
            print(f"Downloading {url} to {filename}...")
            response = requests.get(url)
            response.raise_for_status()
            with open(filename, "wb") as f:
                f.write(response.content)
        print("Download completed sucessfully.")

download_the_data=Loader()