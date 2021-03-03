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
import uuid
import shutil

files = glob.glob("data/*.txt")

for file in files:
    id = file.split("/")[-1].split("search.txt")[0].replace("atoingashu0", "atoingashu").replace("ajiataikan0", "ajiataikan")

    manifest_path = "../../docs/"+id+"/manifest.json"

    if not os.path.exists(manifest_path):
        print("ファイルが存在しないためスキップします。", file)
        continue

    with open(manifest_path) as f:
        manifest_data = json.load(f)

    manifest = manifest_data["@id"]

    canvases = manifest_data["sequences"][0]["canvases"]

    canvas_map = {}

    for i in range(len(canvases)):

        canvas  = canvases[i]

        thumbnail = canvas["thumbnail"]["@id"]

        image = thumbnail.split("/")[-5]

        if "ajiataikan" in file:
            image = int(image.split(".")[0].split("-")[0].split("_")[1])
        elif "atoingashu" in file:
            image = int(image.split(".")[0].split("-")[0])
        else:
            image = -1

        if image not in canvas_map:
            canvas_map[image] = {
                "id" : canvases[i]["@id"],
                "width" : canvases[i]["width"],
                "height" : canvases[i]["height"],
                "image" : thumbnail
            }

    # print(canvas_map)

    text_map = {}

    with open(file) as f:
        l_strip = [s.strip() for s in f.readlines()]

        for l in l_strip:
            sp = l.split("\t")

            page = sp[0].split(".")[0].split("-")[0]

            page = page.strip()[-3:]

            page = int(page)
            text = sp[1]

            if page not in text_map:
                text_map[page] = []

            text_map[page].append(text)

        soup = BeautifulSoup(open("template.xml",'r'), "xml")

        facsimile = soup.new_tag("facsimile")
        soup.find("TEI").append(facsimile)

        surfaceGrp = soup.new_tag("surfaceGrp", facs=manifest)
        facsimile.append(surfaceGrp)

        
        for page in text_map:

            canvas = canvas_map[page]

            surface = soup.new_tag("surface")
            surfaceGrp.append(surface)

            graphic = soup.new_tag("graphic", n=canvas["id"], url=canvas["image"])
            surface.append(graphic)

            for text in text_map[page]:

                uuid2 = "zone_" + str(uuid.uuid4())

                zone = soup.new_tag("zone", lrx=canvas["width"], lry=canvas["height"], ulx="0", uly="0")
                zone["xml:id"]  = uuid2
                surface.append(zone)
                
                span = soup.new_tag("span", facs="#"+uuid2)
                span.append(text)
                soup.find("body").find("p").append(span)

        soup.find("title").append(manifest_data["label"])
        

        html = soup.prettify("utf-8")


        path = "../../docs/files/tei/"+id+"/search.xml"

        odir = os.path.dirname(path)

        os.makedirs(odir, exist_ok=True)

        with open(path, "wb") as file:
            file.write(html)

        tei_url = path.replace("../../docs", "https://toyo-bunko.github.io/iiif")

        manifest_data["service"] = {
            "@context": "http://iiif.io/api/search/0/context.json",
            "@id": "https://w3id.org/dhj/i3sa/"+tei_url,
            "profile": "http://iiif.io/api/search/0/search",
            "label": "Search within this manifest"
        }

        copy_path = manifest_path+"_org.json"

        if not os.path.exists(copy_path):
            shutil.copyfile(manifest_path, copy_path)

        f2 = open(manifest_path, 'w')
        json.dump(manifest_data, f2, ensure_ascii=False, indent=4,
                sort_keys=True, separators=(',', ': '))

    # break


