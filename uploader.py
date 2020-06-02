#!/usr/bin/env python3
import os
import json
import mimetypes

import exifread
import requests
from dateutil import parser

TOKEN = os.environ["UPLOADER_TOKEN"]

START_URL = "https://cloud-api.yandex.net:443/v1/disk"

SYNC_PATH="/photo.sync"
HEADERS = {
    "Authorization": "OAuth {}".format(TOKEN)
}

s = requests.Session()
s.headers.update(HEADERS)

resp = s.get(
    START_URL
)


assert resp.ok, resp.reason
parsed = resp.json()
name = parsed["user"]["display_name"]

print("Logged in as", name)

resp = s.get(
    START_URL + "/resources?path={}".format(SYNC_PATH),
)
parsed = resp.json()

for item in parsed["_embedded"]["items"]:
    print(item["name"])

def isimage(path):
    if not os.path.exists(path):
        return False
    t, enc = mimetypes.guess_type(path)
    if not t:
        return False
    return t.startswith("image")


def mkdirs(path):
    print("Creating '{}'".format(path))
    if not path or path == "/":
        return
    resp = s.get(START_URL + "/resources?path={}".format(path))
    if resp.ok:
        print(resp.status_code, path, "exists")
        return
    print("'{}' doesn't esitst, {}".format(path, resp.status_code))
    print(resp.json())

    mkdirs(os.path.dirname(path))
    resp = s.put(
        START_URL + "/resources?path={}".format(path))
    assert resp.ok, (resp.reason, resp.text)


for path, dirs, files in os.walk("/media/petrovev/EOS_DIGITAL"):
    images = [f for f in files if isimage(os.path.join(path, f))]
    if images:
        print(path)
        for image in images:
            img_path  = os.path.join(path, image)
            with open(img_path, 'rb') as f:
                tags = exifread.process_file(f, details=False, stop_tag="DateTimeOriginal")
            
            date_time = parser.parse(str(tags["EXIF DateTimeOriginal"]))
            image_dir = SYNC_PATH + "/" + date_time.strftime("%Y/%m/%d")
            mkdirs(image_dir)
            
            upload_path = "{}/{}".format(image_dir, image)
            print("\t", image, upload_path)
            resp = s.get(
                START_URL + "/resources/upload?overwrite=false&path={}".format(upload_path))
            assert resp.ok, resp.reason
            
            upload_url = resp.json()["href"]
            with open(img_path, 'rb') as f:
                resp = s.put(
                    upload_url, data=f)
                assert resp.ok, resp.reason
