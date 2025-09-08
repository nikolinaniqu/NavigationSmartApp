import aiohttp
import asyncio
import os
from spypointapi import SpypointApi

LOCAL_FOLDER = "spypoint_images"

async def download_images():
    os.makedirs(LOCAL_FOLDER, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        api = SpypointApi("andreas.senn@copernitech.com", "823-fweJäfwef3D", session)
        cameras = await api.async_get_cameras()
        print(cameras)
asyncio.run(download_images())
#         for camera in cameras:
#             photos =
#             for photo in photos:
#                 url = photo.get('full_hd_url') or photo.get('url')
#                 filename = os.path.join(LOCAL_FOLDER, os.path.basename(url))
#                 print(f"Downloading {url} to {filename} ...")
#                 async with session.get(url) as resp:
#                     resp.raise_for_status()
#                     with open(filename, "wb") as f:
#                         f.write(await resp.read())
#     print("Download complete.")
#
# asyncio.run(download_images())
