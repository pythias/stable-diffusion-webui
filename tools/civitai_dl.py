import requests
import json
import os
import tempfile
import argparse
import shutil
import zlib

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__) , "../"))

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}

proxies = {
    "http": "http://100.72.64.19:12798",
    "https": "http://100.72.64.19:12798",
}

folders = {}

url_by_id = "https://civitai.com/api/v1/models/"
url_by_hash = "https://civitai.com/api/v1/model-versions/by-hash/"
url_by_version_id = "https://civitai.com/api/v1/model-versions/"

model_type_paths = {
    "Checkpoint": "models/Stable-diffusion",
    "TextualInversion": "embeddings",
    "Hypernetwork": "models/hypernetworks",
    "LORA": "models/Lora",
    "LoCon": "models/Lora",
}

def log(msg):
    print(f"Civitai Downloader v0.0.1: {msg}")

def get_model_info(id: str) -> dict:
    log("Request model info from civitai")

    r = requests.get(url_by_id+str(id), headers=headers, proxies=proxies)
    if not r.ok:
        if r.status_code == 404:
            log("Civitai does not have this model")
        else:
            log("Http error, code: " + str(r.status_code) + ", response:" + r.text)
        return

    model_info = r.json()
    if model_was_valid(model_info=model_info):
        return model_info

    return

def dict_has_keys(dict: dict, keys: list) -> bool:
    if not dict:
        log("dict is None")
        return False

    if not keys:
        log("keys is None")
        return False

    for key in keys:
        if key not in dict.keys():
            log(f"key {key} is not in dict")
            return False

    return True

# check if model is valid
def model_was_valid(model_info: dict) -> bool:
    if not model_info:
        log("model_info is None")
        return False

    if not dict_has_keys(model_info, ["name", "type", "modelVersions"]):
        return False

    if not dict_has_keys(model_type_paths, [model_info["type"]]):
        return False

    return True


def crc32_hash_file(file_path):
    # Initialize the CRC32 value
    crc = 0

    # Read the file in binary mode and update the CRC32 value in chunks
    with open(file_path, 'rb') as file:
        for data in iter(lambda: file.read(8192), b''):
            crc = zlib.crc32(data, crc)

    # Ensure the CRC32 value is unsigned
    return crc & 0xFFFFFFFF

def download_model(model_id: str) -> tuple:
    model_info = get_model_info(model_id)
    if model_info is None or model_info == {}:
        log(f"Can't get model info, id:{model_id}")
        return

    model_name = model_info['name']
    model_type = model_info["type"]
    model_file = model_info["modelVersions"][0]["files"][0]
    download_url = model_file["downloadUrl"]
    download_file = os.path.join(root_path, model_type_paths[model_type], model_file['name'])

    log(f"Model download started, id:{model_id}, name:{model_name}, url:{download_url}")
    dl_file(download_url, download_file)

    model_hash = model_file["hashes"]["CRC32"]
    downloaded_hash = crc32_hash_file(download_file)
    if downloaded_hash != model_hash:
        log(f"Downloaded model file is broken, id:{model_id}, name:{model_name}, url:{download_url}, hash:{model_hash}, crc32:{downloaded_hash}")
    else:
        log(f"Download model success, id:{model_id}, name:{model_name}, url:{download_url}")

def dl_file(url, filepath=None):
    new_headers = headers.copy()

    folder = os.path.dirname(filepath)
    if not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(filepath):
        downloaded_size = os.path.getsize(filepath)
        log(f"Model already exists, path:{filepath}, size:{downloaded_size}")
        new_headers['Range'] = f'bytes={downloaded_size}-'

    with requests.get(url, stream=True, verify=False, headers=new_headers, proxies=proxies) as r:
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--id', type=int, default=-1)
    args.add_argument('-p', '--proxy', type=str, default="")
    args.add_argument('-r', '--root', type=str, default="")

    opt = args.parse_args()

    if opt.id == -1:
        log("Please specify the model id")
        exit(1)

    if opt.proxy:
        proxies = {
            "http": opt.proxy,
            "https": opt.proxy,
        }

    if opt.root:
        root_path = opt.root

    download_model(f"{opt.id}")
