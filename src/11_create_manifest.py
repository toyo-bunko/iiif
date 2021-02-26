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

prefix = "https://toyo-bunko.github.io/iiif"
path = "data/atoinga.xlsx"
odir = "../docs"

'''
config_path = "/Users/nakamura/git/min_a/lda/src/data/config.yml"
f = open(config_path, "r+")
config = yaml.load(f)

image_api = config["prefix"]
data_dir = config["src_dir"] +"/data"
path_metadata = data_dir+"/metadata.xlsx"
path_image = data_dir+"/images.xlsx"
manifest_dir = "/data/manifest/"
doc_dir = config["doc_dir"]
odir = doc_dir+ manifest_dir
prefix = image_api + manifest_dir

'''
def get_id_image_map(df_media):

    map = {}

    r_count = len(df_media.index)

    for j in range(1, r_count):

        id = df_media.iloc[j, 0]

        if id not in map:
            map[id] = []

        map[id].append({
            "original": df_media.iloc[j, 1],
            "thumbnail": df_media.iloc[j, 2],
            "width": int(df_media.iloc[j, 3]) if not pd.isnull(df_media.iloc[j, 3]) else -1,
            "height": int(df_media.iloc[j, 4]) if not pd.isnull(df_media.iloc[j, 4]) else -1,
        })

    return map

def get_id_toc_map(df_toc):

    map = {}

    r_count = len(df_toc.index)

    for j in range(1, r_count):

        id = df_toc.iloc[j, 0]

        if id not in map:
            map[id] = []

        map[id].append({
            "page": int(df_toc.iloc[j, 1]),
            "toc": df_toc.iloc[j, 2]
        })

    return map


df_item = pd.read_excel(path, sheet_name="item", header=None, index_col=None, engine="openpyxl")
df_media = pd.read_excel(path, sheet_name="media", header=None, index_col=None, engine="openpyxl")
df_toc = pd.read_excel(path, sheet_name="toc", header=None, index_col=None, engine="openpyxl")

r_count = len(df_item.index)
c_count = len(df_item.columns)

'''
viewingDirection = "right-to-left"
logo = "https://nakamura196.github.io/lda/assets/images/favicon.ico"
within = "https://nakamura196.github.io/lda/"
attribution = "地域文化資源デジタルアーカイブ"
license = "http://creativecommons.org/licenses/by/4.0/"
'''

id_image_map = get_id_image_map(df_media)
id_toc_map = get_id_toc_map(df_toc)

map = {}

for i in range(0, c_count):
    label = df_item.iloc[0, i]
    uri = df_item.iloc[1, i]
    # type = df.iloc[2, i]
    target=df_item.iloc[3,i]

    if target == "metadata":
        obj = {}
        map[i] = obj
        obj["label"] = label

    if uri == "http://purl.org/dc/terms/rights":
        license_index = i
    if uri == "http://purl.org/dc/terms/title":
        title_index = i
    if uri == "http://purl.org/dc/terms/description":
        description_index = i
    if uri == "http://www.w3.org/2000/01/rdf-schema#seeAlso":
        seeAlso_index = i
    if uri == "http://purl.org/dc/terms/identifier":
        identifier_index = i
    if label == "logo":
        logo_index = i
    if label == "attribution":
        attribution_index = i
    if label == "within":
        within_index = i
    if label == "viewingDirection":
        viewingDirection_index = i
    if label == "viewingHint":
        viewingHint_index = i
    if uri == "http://purl.org/dc/terms/relation":
        related_index = i
    if label == "manifest":
        manifest_index = i

for j in range(4, r_count):

    

    # seeAlso = df_item.iloc[j, seeAlso_index]

    id = df_item.iloc[j, identifier_index]

    print(str(j)+"/"+str(r_count), id)

    # manifest_uri = seeAlso.replace("/json/", "/manifest/")

    manifest_uri = df_item.iloc[j, manifest_index]

    # relation = "http://da.dl.itc.u-tokyo.ac.jp/uv/?manifest="+manifest_uri
    relation = df_item.iloc[j, related_index]

    title = df_item.iloc[j, title_index]

    metadata = []
    for index in map:
        value = df_item.iloc[j, index]
        if not pd.isnull(value) and value != 0:
            values = value.split(",")
            for value in values:
                metadata.append({
                    "label": map[index]["label"],
                    "value" : value.strip()
                })

    viewingHint = "non-paged"
    if viewingHint_index != None:
        value = df_item.iloc[j, viewingHint_index]
        if value == "http://iiif.io/api/presentation/2#pagedHint":
            viewingHint = "paged"

    manifest = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@type": "sc:Manifest",
        "@id": manifest_uri,
        "license": df_item.iloc[j, license_index],
        # "attribution": df_item.iloc[j, attribution_index],
        "label": title,
        # "logo": df_item.iloc[j, logo_index],
        # "within": df_item.iloc[j, within_index],
        # "viewingDirection": df_item.iloc[j, viewingDirection_index],
        # "seeAlso": seeAlso,
        
        "sequences": [
            {
                "@type": "sc:Sequence",
                "@id": manifest_uri.replace("/manifest.json", "")+"/sequence/normal",
                "label": "Current Page Order",
                "viewingHint": viewingHint,
                "canvases": []
            }
        ]
    }

    if not pd.isnull(relation):
        manifest["related"] = relation

    fields = [
        {
            "key": description_index,
            "label": "description"
        },
        {
            "key": attribution_index,
            "label": "attribution"
        }
    ]

    viewingDirection = "left-to-right"
    if viewingDirection_index != None:
        value = df_item.iloc[j, viewingDirection_index]
        if value == "http://iiif.io/api/presentation/2#rightToLeftDirection":
            viewingDirection = "right-to-left"
    manifest["viewingDirection"] = viewingDirection

    

    if len(metadata) > 0:
        manifest["metadata"] = metadata

    for obj in fields:

        if obj["key"] != None:
            value = df_item.iloc[j, obj["key"]]
            if not pd.isnull(value) and value != 0:
                manifest[obj["label"]] = value

    canvases = manifest["sequences"][0]["canvases"]

    
    if id in id_image_map:

        images = id_image_map[id]
        for i in range(len(images)):

            img_obj = images[i]

            img_url = img_obj["original"]

            if "info.json" in img_url:

                try:

                    r = requests.get(img_url)
                    info = r.json()

                except Exception as e:
                    print(img_url, e)
                    continue

                image_api = img_url.replace("/info.json", "")

                

                width = info["width"]
                height = info["height"]

                service = {
                    "@context": info["@context"],
                    "@id": image_api,
                    "profile": info["profile"][0]
                }

                img_id = image_api+"/full/full/0/default.jpg"

                thumbnail = {
                    "@id": image_api+"/full/"+str(info["sizes"][0]["width"])+",/0/default.jpg",
                    "service" : service
                }

            else:
                img_id = img_url

                thumbnail = {
                    "@id": img_obj["thumbnail"]
                }

                width = img_obj["width"]
                height = img_obj["height"]

            canvas_id = manifest_uri.replace("/manifest.json", "")+"/canvas/p"+str(i+1)

            canvas_label = "["+str(i+1)+"]"

            canvas = {
                "@type": "sc:Canvas",
                "@id": canvas_id,
                "label": canvas_label,
                "thumbnail": thumbnail,
                "images": [
                    {
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "@id": manifest_uri.replace("/manifest.json", "") + "/annotation/p"+str(i+1)+"-image",
                        "resource": {
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                            "width" : width,
                            "height" : height,
                            "@id": img_id
                        },
                        "on": canvas_id
                    }
                ],
                "width": width,
                "height": height
            }

            if i == 0:
                manifest["thumbnail"] = thumbnail

            if "info.json" in img_url:
                canvas["thumbnail"]["service"] = service
                canvas["images"][0]["resource"]["service"] = service
                # canvas["images"][0]["resource"]["service"]["width"] = width
                # canvas["images"][0]["resource"]["service"]["height"] = height

            canvases.append(canvas)

    if id in id_toc_map:
        tocs = id_toc_map[id]
        structures = []
        for i in range(len(tocs)):
            toc_obj = tocs[i]
            page = toc_obj["page"]
            toc = toc_obj["toc"]

            range_id = manifest_uri.replace("/manifest.json", "") + "/range/r" + str(page)

            try:
                canvas_id = canvases[page-1]["@id"]

                obj = {
                    "@id": range_id,
                    "@type": "sc:Range",
                    "canvases": [
                        canvas_id
                    ],
                    "label": toc
                }
                structures.append(obj)

            except Exception as e:
                print(e)

        if len(structures) > 0:
            manifest["structures"] = structures


    opath = manifest_uri.replace(prefix, odir)
    tmp = os.path.split(opath)

    os.makedirs(tmp[0], exist_ok=True)

    f2 = open(opath, 'w')
    json.dump(manifest, f2, ensure_ascii=False, indent=4,
              sort_keys=True, separators=(',', ': '))

