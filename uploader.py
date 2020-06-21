#!/usr/bin/env python3
import os
import mimetypes

import exifread
import requests
from datetime import datetime

START_URL = "https://cloud-api.yandex.net:443/v1/disk"

SYNC_PATH = "/photo.sync"


def create_session():
    token = os.environ["UPLOADER_TOKEN"]
    HEADERS = {
        "Authorization": "OAuth {}".format(token)
    }

    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def isimage(path):
    if not os.path.exists(path):
        return False
    t, enc = mimetypes.guess_type(path)
    if not t:
        return False
    return t.startswith("image")


def shot_date(path):
    with open(path, 'rb') as f:
        tags = exifread.process_file(f, details=False, stop_tag="DateTimeOriginal")

    return datetime.strptime(str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")


def mkdirs(s, path):
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
    s = create_session()
    if images:
        print(path)
        for image in images:
            img_path = os.path.join(path, image)
            date_time = shot_date(img_path)
            image_dir = SYNC_PATH + "/" + date_time.strftime("%Y/%m/%d")
            mkdirs(s, image_dir)

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
