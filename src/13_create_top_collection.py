import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image
import yaml
import requests
import glob

prefix = "https://toyo-bunko.github.io/iiif"
odir = "../docs"

files = glob.glob("../docs/collection/*.json")

collections = []

for file in files:
    if "top.json" not in file:
        with open(file) as f:
            df = json.load(f)

        collections.append({
            "@id" : df["@id"],
            "@type" : "sc:Collection",
            "label" : df["label"]
        })

collection_url = prefix + "/collection/top.json"
    
collection = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": collection_url,
    "@type": "sc:Collection",
    "label": "東洋文庫IIIFコレクション",
    "collections": collections
}

opath = collection_url.replace(prefix, odir)
tmp = os.path.split(opath)

os.makedirs(tmp[0], exist_ok=True)

f2 = open(opath, 'w')
json.dump(collection, f2, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))

