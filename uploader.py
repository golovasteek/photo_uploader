#!/usr/bin/env python3
import requests
import os
import json

TOKEN = os.environ["UPLOADER_TOKEN"]

START_URL = "https://cloud-api.yandex.net:443/v1/disk"

resp = requests.get(
    START_URL,
    headers = {
        "Authorization": "OAuth {}".format(TOKEN)
    }
)

assert resp.ok
parsed = resp.json()
name = parsed["user"]["display_name"]

print(name)
